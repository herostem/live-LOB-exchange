from LimitOrderBook import LOB
import random

class Market:
    def __init__(self, 
                 initialBid, initialAsk,
                 LOB = LOB(lotSize=1, epsilon=1, tickSize=1),  
                 LMT_arrivalParams = {"omega": 1.3, "k": 1.0, 
                                      "MAX_DISTANCE": 20, "MIN_DISTANCE": 1, "MAX SIZE": 50},
                 MKT_arrivalParams = {"mu": 0.4, "MAX SIZE": 30},
                 rerunParams = {"priceDelta": 2.0, "sizeMult": 2},
                 Cancel_arrivalParams = {"omega": 0.7 , "k": 1.0, 
                                         "MAX_DISTANCE": 20, "MIN_DISTANCE": 1}
                 ):
        
        self.LOB = LOB
        self.tradingPrice = 0

        self.initialBid = initialBid
        self.initialAsk = initialAsk
        self.LOB.PlaceOrder(self.initialBid, -1 * self.LOB.lotSize)
        self.LOB.PlaceOrder(self.initialAsk, self.LOB.lotSize)

        self.MKT_arrivalParams = MKT_arrivalParams
        self.LMT_arrivalParams = LMT_arrivalParams
        self.Cancel_arrivalParams = Cancel_arrivalParams
        self.rerunParams = rerunParams

    def __LMTrateFunction(self, distance, side):
        if distance < self.LMT_arrivalParams["MIN_DISTANCE"]:
            return 0
        if distance > self.LMT_arrivalParams["MAX_DISTANCE"]:
            return 0
        
        elif side == "bid":
            i = self.LOB.getRelativePrice(distance, "bid") # change i to price
            if i is None:
                return 0
            rate = self.LMT_arrivalParams["k"] / (i ** self.LMT_arrivalParams["omega"])
        elif side == "ask":
            i = self.LOB.getRelativePrice(distance, "ask")
            if i is None:
                return 0
            rate = self.LMT_arrivalParams["k"] / (i ** self.LMT_arrivalParams["omega"])
        else:
            raise ValueError("Side must be either 'bid' or 'ask'.")
        return rate

    def __CancelRateFunction(self, distance, side):
        if distance < self.Cancel_arrivalParams["MIN_DISTANCE"]:
            return 0
        if distance > self.Cancel_arrivalParams["MAX_DISTANCE"]:
            return 0
        
        elif side == "bid":
            price = self.LOB.getRelativePrice(distance, "bid")
            if price is None:
                return 0
            rate = self.Cancel_arrivalParams["k"] / (price ** self.Cancel_arrivalParams["omega"])
        elif side == "ask":
            price = self.LOB.getRelativePrice(distance, "ask")
            if price is None:
                return 0
            rate = self.Cancel_arrivalParams["k"] / (price ** self.Cancel_arrivalParams["omega"])
        else:
            raise ValueError("Side must be either 'bid' or 'ask'.")
        return rate
    
    def checkLMTrates(self, side):
        for i in range(self.LMT_arrivalParams["MIN_DISTANCE"], self.LMT_arrivalParams["MAX_DISTANCE"] + 1, self.LOB.epsilon): # step by epsilon
            rate = self.__LMTrateFunction(i, side)
            if rate == 0:
                continue

            if random.random() < rate:
                if side == "bid":
                    self.LOB.PlaceOrder(self.LOB.getRelativePrice(i, "bid"),
                                        -1 * random.randrange(self.LOB.lotSize, self.LMT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))
                elif side == "ask":
                    self.LOB.PlaceOrder(self.LOB.getRelativePrice(i, "ask"),
                                        random.randrange(self.LOB.lotSize, self.LMT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))
                
    def checkMKTrates(self):
        rate = self.MKT_arrivalParams["mu"]
        if random.random() < rate:
            if random.random() < 0.5: # 50% chance of bid or ask
                self.LOB.MKTorder(-1 * random.randrange(self.LOB.lotSize, self.MKT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))
            else:
                self.LOB.MKTorder(random.randrange(self.LOB.lotSize, self.MKT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))

    def checkCancelRates(self, side):
        for i in range(self.Cancel_arrivalParams["MIN_DISTANCE"], self.Cancel_arrivalParams["MAX_DISTANCE"] + 1, self.LOB.epsilon): # step by epsilon
            if side == "bid": # scale by num of orders
                x = sum(1 for order in self.LOB.orderSet if order.side == "bid" and 
                        order.price == self.LOB.getRelativePrice(i, "bid"))
            elif side == "ask":
                x = sum(1 for order in self.LOB.orderSet if order.side == "ask" and 
                        order.price == self.LOB.getRelativePrice(i, "ask"))
            rate = self.__CancelRateFunction(i, side) * x
            if rate == 0:
                continue

            if random.random() < rate:
                for order in self.LOB.orderSet:
                    if order.side == side and order.price == self.LOB.getRelativePrice(i,   side):
                        self.LOB.CancelOrder(order)
                        break

    def rerunCheck(self):
        rerun = False
        for item in self.LOB.allStats:
            if item is None:
                rerun = True
                break
        if rerun:
            self.__randomBegin()

    # adds more depth to prices closer to best quotes
    def __randomBegin(self):
        for i in range(10):
            while i > 0:
                self.LOB.PlaceOrder(self.initialBid - i, 
                                    -1 * random.randrange(self.LOB.lotSize, self.LMT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))
                self.LOB.PlaceOrder(self.initialAsk + i, 
                                    random.randrange(self.LOB.lotSize, self.LMT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))
                i -= 1
            
    def __update(self):
        self.rerunCheck()
        self.checkLMTrates("bid")
        self.checkLMTrates("ask")
        self.checkMKTrates()
        self.checkCancelRates("bid")
        self.checkCancelRates("ask")
        self.tradingPrice = self.LOB.lastPrice
        print(f"Bid: {self.LOB.bidPrice}, Ask: {self.LOB.askPrice}, Last Price: {self.LOB.lastPrice}, Spread: {self.LOB.spread}, Mid Price: {self.LOB.midPrice}") # just for testing
            
    def runMarket(self, run_time):
        self.__randomBegin()
        while run_time > 0:
            self.__update()
            run_time -= 1

    