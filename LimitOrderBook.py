from decimal import Decimal
from datetime import datetime

class LOB:
    def __init__(self, lotSize=1, epsilon=1, tickSize=1):
        self.orderSet = []
        self.askSet = []
        self.bidSet = []

        self.bidDepth = {}
        self.askDepth = {}

        self.lotSize = lotSize
        self.epsilon = epsilon
        self.tickSize = tickSize
        self.tickStr = f"{tickSize}"

    def __checkPrice(self, price):
        if price % self.tickSize != 0:
            raise ValueError("Price must be a multiple of the tick size.")
        if price < self.tickSize:
            raise ValueError("Price must be strictly greater than or equal to the tick size.")
        if Decimal(price).as_tuple().exponent != Decimal(self.tickSize).as_tuple().exponent:
            raise ValueError("Price must be specified to the accuracy of the tick size.")
        
    def __checkSize(self, size):
        if size < self.lotSize:
            raise ValueError("Size must be strictly greater than or equal to the lot size.")
        if size % self.epsilon != 0:
            raise ValueError("Size must be an increment of the epsilon.")
        
    def addToSets(self, order):
        if order[1] < 0:
            self.bidSet.append(order)
        elif order[1] > 0:
            self.askSet.append(order)

    @staticmethod
    def PrintOrderRecipt(order):
        print(f"Order placed at {order[2]} | Price = {order[0]} | Units = {order[1]}")

    @staticmethod
    def PrintOrderCancel(price, size, time):
        print(f"Order canceled at {time} | Price = {price} | Units = {size}")

    def PlaceOrder(self, price, size, time=datetime.now()):
        self.__checkPrice(price)
        self.__checkSize(size)

        order = (price, size, time)

        self.orderSet.append(order)
        self.addToSets(order)
        self.PrintOrderRecipt(order)
        self.AddDepth(price, size)

    def CancelOrder(self, price, size, time):
        for order in self.orderSet:
            if order[0] == price and order[1] == size and order[2] == time:
                self.orderSet.remove(order)
                if order[1] > 0:
                    self.bidSet.remove(order)
                elif order[1] < 0:
                    self.askSet.remove(order)
                self.PrintOrderCancel(price, size, time)
                self.RemoveDepth(price, size)
                return
        raise ValueError("Order not found in the order set.")
    
    @property
    def bidPrice(self):
        if not self.bidSet:
            return None
        return max(order[0] for order in self.bidSet)
    
    @property
    def askPrice(self):
        if not self.askSet:
            return None
        return min(order[0] for order in self.askSet)
    
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
                if order[0] == price:
                    return sum(order[1] for order in self.bidSet if order[0] == price)
                else:
                    raise ValueError("Price has no previous depth history.")
        elif side == "ask":
            for order in self.askSet:
                if order[0] == price:
                    return sum(order[1] for order in self.askSet if order[0] == price)
                else:
                    raise ValueError("Price has no previous depth history.")
        else:
            raise ValueError("Side must be either 'bid' or 'ask'.")
        
    def getRelativePrice(self, distance, side):
        if side == "bid":
            return abs(self.bidPrice - distance) if self.bidPrice is not None else None
        elif side == "ask":
            return abs(distance - self.askPrice) if self.askPrice is not None else None
        else:
            raise ValueError("Side must be either 'bid' or 'ask'.")
        
    def getRelativeDepth(self, price, side):
        if side == "bid":
            return self.getDepth(self.getRelativePrice(price, "bid"), "bid")
        elif side == "ask":
            return self.getDepth(self.getRelativePrice(price, "ask"), "ask")
        
    def AddDepth(self, price, size):
        if size < 0:
            self.bidDepth[price] += size
        elif size > 0:
            self.askDepth[price] += size

    def RemoveDepth(self, price, size):
        if size < 0:
            self.bidDepth[price] -= size
        elif size > 0:
            self.askDepth[price] -= size
                       

    