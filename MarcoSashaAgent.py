from Market import Market
import math

class MarcoSashaAgent:
    def __init__(self, LOB, riskAversion = 0.1, timeHorizon = 1):
        self.LOB = LOB

        self.riskAversion = riskAversion
        self.timeHorizon = timeHorizon
        self.omega = self.market.LMT_arrivalParams["omega"]
        self.volatility = 1 # will implement in market later

        self.inventory = [] # all current orders

    @property
    def shares(self): # positive for long, negative for short
        return -1 * sum([order.size for order in self.inventory]) 
    
    def reservationPrice(self, mid, shares):
        return mid - self.riskAversion * self.volatility ** 2 * self.timeHorizon * shares

    def optimalSpread(self):
        return self.riskAversion * self.volatility ** 2 * self.timeHorizon + (2 / self.omega) * math.log(1 + (self.riskAversion / self.omega))