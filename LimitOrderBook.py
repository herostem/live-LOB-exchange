from decimal import Decimal
from datetime import datetime
from Order import Order

class LOB:
    def __init__(self, lotSize=1, epsilon=1, tickSize=1):  # resolution params
        self.orderSet = []
        self.askSet = []
        self.bidSet = []

        self.num = 1 # used for counting orders
        self.lastPrice = 0

        self.bidDepth = {}  # {price: depth available}
        self.askDepth = {}

        self.lotSize = lotSize
        self.epsilon = epsilon
        self.tickSize = tickSize

    def __checkPrice(self, price):
        if price % self.tickSize != 0:
            raise ValueError("Price must be a multiple of the tick size.")
        if price < self.tickSize:
            raise ValueError("Price must be strictly greater than or equal to the tick size.")
        if Decimal(price).as_tuple().exponent != Decimal(self.tickSize).as_tuple().exponent:
            raise ValueError("Price must be specified to the accuracy of the tick size.")
        
    def __checkSize(self, size):
        if abs(size) < self.lotSize:
            raise ValueError("Size must be strictly greater than or equal to the lot size.")
        if size % self.epsilon != 0:
            raise ValueError("Size must be an increment of the epsilon.")
        
    def addToSets(self, order):
        if order.size < 0:
            self.bidSet.append(order)
        elif order.size > 0:
            self.askSet.append(order)

    @staticmethod
    def PrintOrderRecipt(order):
        print(f"Order placed at {order.time} | Price = {order.price} | Units = {order.size}")

    @staticmethod
    def PrintOrderCancel(order):
        print(f"Order canceled at {order.time} | Price = {order.price} | Units = {order.size}")

    @staticmethod
    def PrintOrderFill(order):
        print(f"Order filled at {order.time} | Price = {order.price} | Units = {order.size}")

    @staticmethod
    def PrintPartialOrderFill(order, amt):
        if order.side == "bid":
            amt = -1 * amt
        print(f"Order partially filled at {order.time} | Price = {order.price} | Units Filled = {amt} | Units Remaining = {order.size}")

    def __matchOrders(self, price, size, id):
        order = Order(price, size, id)

        if self.bidPrice is None or self.askPrice is None or self.bidSet is None or self.askSet is None:
            return order

        if size < 0: #bid order match to ask
            if price < self.askPrice:
                return order
            
            usableSize = abs(size)

            # sort orders by ascending price, and time
            sortedAskSet = sorted(self.askSet)
            matchedOrders = []

            for x in sortedAskSet:
                if usableSize == 0: # order filled
                    break
                if x.price > price: # order price too high, cannot match
                    break
            
                if x.size == usableSize:# perfect fill
                    self.fillOrder(x.price, x.size, x.time)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.size > abs(usableSize): # spends all usable size without fully filling order
                    self.partialFillOrder(x, usableSize)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.size < abs(usableSize):
                    matchedOrders.append(x)
                    usableSize = x.removeSize(usableSize)

            for x in matchedOrders:
                if x.isFilled:
                    self.fillOrder(x.price, x.size, x.time)
                    self.lastPrice = x.price
                else:
                    raise ValueError("Unfilled order in matchedOrders list")

            if usableSize != 0:
                return order
            else:
                return None
    
        elif size > 0: #ask order match to bid
            if price > self.bidPrice:
                return order
            
            usableSize = abs(size)
            sortedBidSet = sorted(self.bidSet)
            matchedOrders = []

            for x in sortedBidSet:
                if usableSize == 0:
                    break
                if x.price < price: # order price too low, cannot match
                    break

                if x.size == abs(usableSize):
                    self.fillOrder(x.price, x.size, x.time)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.size > abs(usableSize):
                    self.partialFillOrder(x, usableSize)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.size < abs(usableSize):
                    matchedOrders.append(x)
                    usableSize = x.removeSize(usableSize)

            for x in matchedOrders:
                if x.isFilled:
                    self.fillOrder(x.price, x.size, x.time)
                    self.lastPrice = x.price
                else:
                    raise ValueError("Unfilled order in matchedOrders list")

            if usableSize != 0:
                return order
            else:
                return None
                
        else:
            return order

    def PlaceOrder(self, price, size): # add order matching 
        self.__checkPrice(price)
        self.__checkSize(size)

        order = self.__matchOrders(price, size, self.num)
        if order is None:
            return

        self.lastPrice = order.price
        self.orderSet.append(order)
        self.addToSets(order)
        self.PrintOrderRecipt(order)
        self.AddDepth(price, size)
        self.num += 1

    def CancelOrder(self, order):
        for x in self.orderSet:
            if order == x:
                self.orderSet.remove(order)
                if order.size < 0:
                    self.bidSet.remove(order)
                elif order.size > 0:
                    self.askSet.remove(order)
                self.PrintOrderCancel(order.price, order.size, order.time)
                self.RemoveDepth(order.price, order.size)
                return
        raise ValueError("Order not found in the order set.")
    
    def fillOrder(self, order):
        for x in self.orderSet:
            if order == x:
                self.orderSet.remove(order)
                if order.size < 0:
                    self.bidSet.remove(order)
                elif order.size > 0:
                    self.askSet.remove(order)
                self.PrintOrderFill(order.price, order.size, order.time)
                self.RemoveDepth(order.price, order.size)
                return
        raise ValueError("Order not found in the order set.")

    def partialFillOrder(self, order, delta):
        self.__checkSize(delta)
        for x in self.orderSet:
            if order == x:
                order.removeSize(delta)

        if order.filled:
            self.fillOrder(order)
            self.RemoveDepth(order.price, delta)
        else:
            self.PrintPartialOrderFill(order, delta)
    
    def MKTorder(self, size):
        if size < 0: #bid order match to ask
            if self.askSet is None:
                return

            usableSize = abs(size)
            sortedAskSet = sorted(self.askSet) # ascending order
            matchedOrders = []

            for x in sortedAskSet:
                if usableSize == 0:
                    break

                elif x.size == abs(usableSize):
                    self.fillOrder(x)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.size > abs(usableSize):
                    self.partialFillOrder(x, usableSize)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.size < abs(usableSize):
                    matchedOrders.append(x)
                    usableSize = x.removeSize(usableSize) # usable size negative, ask order size positive

            for x in matchedOrders:
                if x.isFilled:
                    self.fillOrder(x)
                    self.lastPrice = x.price
                else:
                    raise ValueError("Unfilled order in matchedOrders list")

            if usableSize != 0:
                if self.askPrice is None:
                    return
                self.PlaceOrder(self.bidPrice, usableSize)
                return 
            else:
                return 
            
        elif size > 0: #ask order match to bid
            if self.bidSet is None:
                return

            usableSize = abs(size)
            sortedBidSet = sorted(self.bidSet) # descending order
            matchedOrders = []

            for x in sortedBidSet: # descending order
                if usableSize == 0:
                    break
                
                elif x.size == abs(usableSize):
                    self.fillOrder(x)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.size > abs(usableSize):
                    self.partialFillOrder(x, usableSize)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.size < abs(usableSize):
                    matchedOrders.append(x)
                    usableSize = x.removeSize(usableSize) # usable size positive, bid order size negative

            for x in matchedOrders:
                if x.isFilled:
                    self.fillOrder(x)
                    self.lastPrice = x.price
                else:
                    raise ValueError("Unfilled order in matchedOrders list")

            if usableSize != 0:
                if self.bidPrice is None:
                    return
                self.PlaceOrder(self.askPrice, usableSize)
                return 
            else:
                return 
    
    @property
    def bidPrice(self):
        if not self.bidSet:
            return None
        return max(order.price for order in self.bidSet)
    
    @property
    def askPrice(self):
        if not self.askSet:
            return None
        return min(order.price for order in self.askSet)
    
    @property
    def spread(self):
        if self.bidPrice is None or self.askPrice is None:
            return None
        return self.askPrice - self.bidPrice
    
    @property
    def midPrice(self):
        if self.bidPrice is None or self.askPrice is None:
            return None
        return (self.bidPrice + self.askPrice) / 2
    
    # could also just use the depth dicts, but this is explicit method
    def getDepth(self, price, side):
        if side == "bid":
            for order in self.bidSet:
                if order.price == price:
                    return sum(order.size for order in self.bidSet if order.price == price)
                else:
                    raise ValueError("Price has no previous depth history.")
        elif side == "ask":
            for order in self.askSet:
                if order.price == price:
                    return sum(order.size for order in self.askSet if order.price == price)
                else:
                    raise ValueError("Price has no previous depth history.")
        else:
            raise ValueError("Side must be either 'bid' or 'ask'.")
        
    def getRelativePrice(self, distance, side):
        if side == "bid":
            return self.bidPrice - distance if self.bidPrice is not None else None
        elif side == "ask":
            return abs(distance - self.askPrice) if self.askPrice is not None else None
        else:
            raise ValueError("Side must be either 'bid' or 'ask'.")
        
    def getRelativeDepth(self, distance, side):
        if side == "bid":
            return self.getDepth(self.getRelativePrice(distance, "bid"), "bid")
        elif side == "ask":
            return self.getDepth(self.getRelativePrice(distance, "ask"), "ask")
        
    def AddDepth(self, price, size):
        if size < 0:
            self.bidDepth[f"{price}"] = self.bidDepth.get(f"{price}", 0) + size
        elif size > 0:
            self.askDepth[f"{price}"] = self.askDepth.get(f"{price}", 0) + size

    def RemoveDepth(self, price, size):
        if size < 0:
            self.bidDepth[f"{price}"] = self.bidDepth.get(f"{price}", 0) - size
        elif size > 0:
            self.askDepth[f"{price}"] = self.askDepth.get(f"{price}", 0) - size

    @property
    def allStats(self):
        return [
            self.bidPrice,
            self.askPrice,
            self.lastPrice,
            self.spread,
            self.midPrice,
            self.askDepth,
            self.bidDepth
        ]

    