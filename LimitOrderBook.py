import heapq
from Order import Order

class LOB:
    def __init__(self, lotSize=1, epsilon=0.1, tickSize=0.01):  # resolution params
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
        if not round(price / self.tickSize, 8).is_integer():
            raise ValueError("Price must be a multiple of the tick size.")
        if price < self.tickSize:
            raise ValueError("Price must be strictly greater than or equal to the tick size.")

    def __checkSize(self, size):
        if abs(size) < self.lotSize:
            raise ValueError("Size must be strictly greater than or equal to the lot size.")
        if not round(abs(size) / self.epsilon, 8).is_integer():
            raise ValueError("Size must be an increment of the epsilon.")
        
    def addToSets(self, order):
        if order.size < 0:
            heapq.heappush(self.bidSet, order) # auto sorts by price and time
        elif order.size > 0:
            heapq.heappush(self.askSet, order)

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

        if size < 0: #bid order match to ask
            if self.askPrice is None or self.askSet is None: # check opposite side
                return order
            if price < self.askPrice:
                return order
            usableSize = abs(size)
            # checks size, and if the best asks are lower than or eq to the bid order price
            while usableSize > 0 and self.askSet and self.askSet[0].price <= price:
                x = self.askSet[0]
                if x.isFilled:
                    heapq.heappop(self.askSet)
                    continue
                if x.quantity == usableSize:# perfect fill
                    self.fillOrder(x)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.quantity > abs(usableSize): # spends all usable size without fully filling order
                    self.partialFillOrder(x, usableSize)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.quantity < abs(usableSize):
                    usableSize -= x.quantity
                    self.fillOrder(x) # sets size 0
                    self.lastPrice = x.price
            if usableSize != 0:
                return order
            else:
                return None
    
        elif size > 0: #ask order match to bid
            if self.bidPrice is None or self.bidSet is None: # check opposite side
                return order
            if price > self.bidPrice:
                return order
            usableSize = abs(size)
            # the best bid prices must be greater than or equal to the ask order price
            while usableSize > 0 and self.bidSet and self.bidSet[0].price >= price:
                x = self.bidSet[0]
                if x.isFilled:
                    heapq.heappop(self.bidSet)
                    continue
                if x.quantity == abs(usableSize):
                    self.fillOrder(x)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.quantity > abs(usableSize):
                    self.partialFillOrder(x, usableSize)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.quantity < abs(usableSize):
                    usableSize -= x.quantity
                    self.fillOrder(x)
                    self.lastPrice = x.price
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
        self.orderSet.append(order) # no heap needed for orderSet
        self.addToSets(order) # uses heap
        self.PrintOrderRecipt(order)
        self.AddDepth(price, order.size, order.side)
        self.num += 1

    # sets order size to 0
    def CancelOrder(self, order):
        for x in self.orderSet:
            if order == x:
                self.orderSet.remove(order)
                self.PrintOrderCancel(order)
                self.RemoveDepth(order.price, order.size, order.side)
                if not order.isFilled:
                    order.size = 0
                return
        raise ValueError("Order to be canceled not found in the order set.")

    # sets order size to 0
    def fillOrder(self, order):
        for x in self.orderSet:
            if order == x:
                self.orderSet.remove(order)
                self.PrintOrderFill(order)
                self.RemoveDepth(order.price, order.size, order.side)
                if not order.isFilled:
                    order.size = 0
                return
        raise ValueError("Order to be filled not found in the order set.")

    # modifies size
    def partialFillOrder(self, order, delta):
        self.__checkSize(delta)
        for x in self.orderSet:
            if order == x:
                self.RemoveDepth(order.price, delta, order.side)
                order.removeSize(delta)

                if order.isFilled:
                    self.fillOrder(order)
                else:
                    self.PrintPartialOrderFill(order, delta)
                return
        raise ValueError("Order to be partially filled not found in the order set.")
    
    def MKTorder(self, size):
        if size < 0: #bid order match to ask
            if self.askSet is None:
                return

            usableSize = abs(size)
            while usableSize > 0 and self.askSet:
                x = self.askSet[0]
                if x.isFilled:
                    heapq.heappop(self.askSet)
                    continue

                if x.quantity == abs(usableSize):
                    self.fillOrder(x)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.quantity > abs(usableSize):
                    self.partialFillOrder(x, usableSize)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.quantity < abs(usableSize):
                    usableSize -= x.quantity
                    self.fillOrder(x)
                    self.lastPrice = x.price
            if usableSize != 0:
                if self.bidPrice is None:
                    return
                self.PlaceOrder(self.bidPrice, -1 * usableSize)
                return 
            else:
                return 
            
        elif size > 0: #ask order match to bid
            if self.bidSet is None:
                return

            usableSize = abs(size)
            while usableSize > 0 and self.bidSet:
                x = self.bidSet[0]
                if x.isFilled:
                    heapq.heappop(self.bidSet)
                    continue

                if x.quantity == abs(usableSize):
                    self.fillOrder(x)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.quantity > abs(usableSize):
                    self.partialFillOrder(x, usableSize)
                    self.lastPrice = x.price
                    usableSize = 0
                    break
                elif x.quantity < abs(usableSize):
                    usableSize -= x.quantity
                    self.fillOrder(x)
                    self.lastPrice = x.price
            if usableSize != 0:
                if self.askPrice is None:
                    return
                self.PlaceOrder(self.askPrice, usableSize)
                return 
            else:
                return 
    
    @property
    def bidPrice(self):
        while self.bidSet and self.bidSet[0].isFilled:
            heapq.heappop(self.bidSet)

        if not self.bidSet:
            return None
        return self.bidSet[0].price
    
    @property
    def askPrice(self):
        while self.askSet and self.askSet[0].isFilled:
            heapq.heappop(self.askSet)

        if not self.askSet:
            return None
        return self.askSet[0].price
    
    @property
    def spread(self):
        if self.bidPrice is None or self.askPrice is None:
            return None
        return round(self.askPrice - self.bidPrice, 8)
    
    @property
    def midPrice(self):
        if self.bidPrice is None or self.askPrice is None:
            return None
        return round((self.bidPrice + self.askPrice) / 2, 8)
    
    # could also just use the depth dicts, but this is explicit method
    def getDepth(self, price, side):
        if side == "bid":
            return sum(order.size for order in self.bidSet if order.price == price)
        elif side == "ask":
            return sum(order.size for order in self.askSet if order.price == price)
        else:
            raise ValueError("Side must be either 'bid' or 'ask'.")
        
    def getRelativePrice(self, tickDistance, side):
        priceDelta = tickDistance * self.tickSize
        if side == "bid":
            return round(self.bidPrice - priceDelta, 8) if self.bidPrice is not None else None
        elif side == "ask":
            return round(priceDelta + self.askPrice, 8) if self.askPrice is not None else None
        else:
            raise ValueError("Side must be either 'bid' or 'ask'.")
        
    def getRelativeDepth(self, distance, side):
        if side == "bid":
            return self.getDepth(self.getRelativePrice(distance, "bid"), "bid")
        elif side == "ask":
            return self.getDepth(self.getRelativePrice(distance, "ask"), "ask")

    def AddDepth(self, price, delta, side):
        if side == "bid":
            self.bidDepth[f"{price}"] = self.bidDepth.get(f"{price}", 0) - abs(delta)
        elif side == "ask":
            self.askDepth[f"{price}"] = self.askDepth.get(f"{price}", 0) + abs(delta)

    def RemoveDepth(self, price, delta, side):
        if side == "bid":
            self.bidDepth[f"{price}"] = self.bidDepth.get(f"{price}", 0) + abs(delta)
        elif side == "ask":
            self.askDepth[f"{price}"] = self.askDepth.get(f"{price}", 0) - abs(delta)

    def findOrder(self, id):
        for order in self.orderSet:
            if order.id == id:
                return order
        return None

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

    