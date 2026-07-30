from Market import Market
import math

class MarcoSashaAgent: # is not concerned with P&L
    def __init__(self, LOB, omega, riskAversion = 0.1, timeHorizon = 1, stdSize = 20, maxINV = 200):
        self.LOB = LOB

        self.riskAversion = riskAversion
        self.timeHorizon = timeHorizon
        self.omega = omega # use the market LMT arrival param
        self.volatility = 1 # will implement in market later

        self.inventory = [] # all current orders
        self.currentBidPrice = 0
        self.currentAskPrice = 0

        self.stdSize = stdSize
        self.maxINV = maxINV

    @property
    def shares(self): # positive for long, negative for short
        return -1 * sum([order.size for order in self.inventory]) 
    
    def reservationPrice(self, mid, shares):
        return mid - self.riskAversion * self.volatility ** 2 * self.timeHorizon * shares

    def optimalSpread(self):
        return self.riskAversion * self.volatility ** 2 * self.timeHorizon + (2 / self.omega) * math.log(1 + (self.riskAversion / self.omega))
    def calcSizes(self):
        pctINV = self.shares / self.maxINV
        # if shares positive, bid size decreases, ask size increases
        # if shares negative, bid size increases, ask size decreases
        bidSize = ((self.stdSize * (1 - pctINV)) / self.LOB.epsilon) * self.LOB.epsilon
        askSize = ((self.stdSize * (1 + pctINV)) / self.LOB.epsilon) * self.LOB.epsilon

        if abs(self.shares) >= self.maxINV:
            bidSize = 0
            askSize = 0

        return max(bidSize, self.LOB.lotSize), -1 * max(askSize, self.LOB.lotSize)
