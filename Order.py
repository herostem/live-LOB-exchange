from datetime import datetime

class Order:
    __slots__ = ["price", "size", "id", "time", "side"]
    def __init__(self, price, size, id, time=datetime.now()):
        self.price = price
        self.size = size
        self.id = id
        self.time = time

        if size < 0:
            self.side = "bid"
        elif size > 0:
            self.side = "ask"

    @property
    def quantity(self):
        return round(abs(self.size), 8)

    def __eq__(self, otherOrder):
        return self.id == otherOrder.id

    def __lt__(self, otherOrder): # used for sorting
        if self.side != otherOrder.side:
            return False

        if self.side == "bid": # higher priced orders come first
            if self.price != otherOrder.price:
                return self.price > otherOrder.price
            else: 
                return self.id < otherOrder.id # orders with lower id (earlier orders) come first

        elif self.side == "ask": # lower priced orders come first
            if self.price != otherOrder.price:
                return self.price < otherOrder.price
            else: 
                return self.id < otherOrder.id

    def removeSize(self, delta): # allows for partial fills, returns the remaining quantity of the order
        if delta > self.quantity:
            raise ValueError("Delta cannot be greater than the order's quantity.")
        
        if self.size < 0:
            self.size = round(-1 * (self.quantity - delta), 8)
        else:
            self.size = round(self.quantity - delta, 8)

        return self.quantity

    @property
    def isFilled(self):
        return self.quantity == 0
        


    