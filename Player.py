from LimitOrderBook import LOB

class Player:
    def __init__(self, name, LOB, initialBalance = 100000):
        self.LOB = LOB
        self.name = name

        self.balance = initialBalance
        self.availableBalance = initialBalance
        self.inventory = [] # all current orders

        self.availableOwnedShares = 0
        self.ownedShares = 0
        self.shortShares = 0

    def changeBalance(self, amt): # for manual adjustments to balance, not for order fills
        self.balance += amt
        self.availableBalance += amt

    def addShares(self, order):
        if order.side == "buy":
            self.ownedShares += order.quantity
        else:
            self.shortShares += order.quantity

    def removeShares(self, order):
        if order.side == "buy":
            self.ownedShares -= order.quantity
        else:
            self.shortShares -= order.quantity

    def __manageLMTMoney(self, order): # when orders are hit
        if order.side == "buy":
            self.balance -= order.price * order.quantity
        else:
            self.balance += order.price * order.quantity
            self.availableBalance += order.price * order.quantity

    def inventoryCheck(self):
        for order in self.inventory:
            if order not in self.LOB.orderSet or order.quantity == 0:
                self.inventory.remove(order)
                self.removeShares(order)
                self.__manageLMTMoney(order)

    def PlaceLMTOrder(self, price, shares, side):
        shares = round(shares, 8)
        self.LOB.checkPrice(price)
        self.LOB.checkSize(shares)
        if side == "buy":
            if self.availableBalance < price * shares:
                return
            shares = round(-1 * shares, 8)
            self.availableBalance -= price * shares # money is reserved for the order, but not yet spent
        elif side == "sell":
            if self.availableOwnedShares < shares:
                return # could add option to buy shares immediatly then place the sell LMT
            self.availableOwnedShares -= shares # shares are reserved for the order, but not yet sold
            
        order = self.LOB.PlaceOrder(price, shares)
        if order is None:
            return
        self.addShares(order)
        self.inventory.append(order)

    def PlaceMKTOrder(self, shares, side):
        shares = round(shares, 8)
        self.LOB.checkSize(shares)
        if side == "buy":
            shares = round(-1 * shares, 8)
            if self.availableBalance < self.LOB.askPrice * shares:
                return
            self.availableBalance -= self.LOB.askPrice * shares
            self.balance -= self.LOB.askPrice * shares
        elif side == "sell":
            pass

    def update(self):
        self.inventoryCheck()

  

    