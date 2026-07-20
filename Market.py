from LimitOrderBook import LOB
import random

class Market:
    def __init__(self, 
                 initialBid, initialAsk,
                 LOB = LOB(lotSize=1, epsilon=1, tickSize=1),  
                 LMT_arrivalParams = {"omega": 1.4, "k": 1.0, 
                                      "MAX_DISTANCE": 10, "MIN_DISTANCE": 1, "MAX SIZE": 30},
                 MKT_arrivalParams = {"mu": 0.2, "MAX SIZE": 20},
                 rerunParams = {"priceDelta": 2.0, "sizeMult": 2}
                 ):
        
        self.LOB = LOB
        self.tradingPrice = 0

        self.initialBid = initialBid
        self.initialAsk = initialAsk
        self.LOB.PlaceOrder(self.initialBid, -1 * self.LOB.lotSize)
        self.LOB.PlaceOrder(self.initialAsk, self.LOB.lotSize)

        self.MKT_arrivalParams = MKT_arrivalParams
        self.LMT_arrivalParams = LMT_arrivalParams

        self.rerunParams = rerunParams

    def __LMTrateFunction(self, distance, side):
        if distance < self.LMT_arrivalParams["MIN_DISTANCE"]:
            return 0
        if distance > self.LMT_arrivalParams["MAX_DISTANCE"]:
            return 0
        
        elif side == "bid":
            i = self.LOB.getRelativePrice(distance, "bid")
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
    
    def checkLMTrates(self, side):
        for i in range(self.LMT_arrivalParams["MIN_DISTANCE"], self.LMT_arrivalParams["MAX_DISTANCE"] + 1, self.LOB.epsilon): # step by epsilon
            rate = self.__LMTrateFunction(i, side)
            if rate == 0:
                continue

            if random.random() < rate:
                if side == "bid":
                    self.LOB.PlaceOrder(self.LOB.getRelativePrice(i, "bid"),
                                        -1 * random.randrange(self.LOB.lotSize, self.LMT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))
                    return
                elif side == "ask":
                    self.LOB.PlaceOrder(self.LOB.getRelativePrice(i, "ask"),
                                        random.randrange(self.LOB.lotSize, self.LMT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))
                    return
                
    def checkMKTrates(self):
        rate = self.MKT_arrivalParams["mu"]
        if random.random() < rate:
            if random.random() < 0.5: # 50% chance of bid or ask
                self.LOB.MKTorder(-1 * random.randrange(self.LOB.lotSize, self.MKT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))
            else:
                self.LOB.MKTorder(random.randrange(self.LOB.lotSize, self.MKT_arrivalParams["MAX SIZE"] + 1, self.LOB.epsilon))

    def rerunCheck(self):
        rerun = False

        for item in self.LOB.allStats:
            if item is None:
                rerun = True
                break
        
        if rerun:
            self.LOB.PlaceOrder(self.initialBid - self.rerunParams["priceDelta"], 
                                -1 * self.LOB.lotSize * self.rerunParams["sizeMult"])
            self.LOB.PlaceOrder(self.initialAsk + self.rerunParams["priceDelta"], 
                                self.LOB.lotSize * self.rerunParams["sizeMult"])
            print("Rerun triggered: Placing additional orders to maintain market depth.")
        else:
            return
                
    def __update(self):
        self.rerunCheck()
        self.checkLMTrates("bid")
        self.checkLMTrates("ask")
        self.checkMKTrates()
        self.tradingPrice = self.LOB.lastPrice
        print(f"Bid: {self.LOB.bidPrice}, Ask: {self.LOB.askPrice}, Last Price: {self.LOB.lastPrice}, Spread: {self.LOB.spread}, Mid Price: {self.LOB.midPrice}") # just for testing
            
    def runMarket(self, run_time):
        while run_time > 0:
            self.__update()
            run_time -= 1

    