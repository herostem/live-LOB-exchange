import unittest
from LimitOrderBook import LOB

class TestLOB(unittest.TestCase):

    def setUp(self):
        self.LOB = LOB(lotSize=1, epsilon=1, tickSize=1)

    def test_find_order(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        order1 = self.LOB.findOrder(1)
        order2 = self.LOB.findOrder(2)
        order3 = self.LOB.findOrder(3)

        self.assertIsNotNone(order1)
        self.assertIsNotNone(order2)
        self.assertIsNone(order3)

        self.assertEqual(order1.price, 90)
        self.assertEqual(order1.size, -5)
        self.assertEqual(order2.price, 100)
        self.assertEqual(order2.size, 10)

    def test_getDepth(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.assertEqual(self.LOB.getDepth(90, "bid"), -5)
        self.assertEqual(self.LOB.getDepth(100, "ask"), 10)

    def test_depth_dicts(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.assertEqual(self.LOB.bidDepth["90"], -5)
        self.assertEqual(self.LOB.askDepth["100"], 10)

    def test_place_LMT_order(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.assertEqual(self.LOB.bidDepth["90"], -5)
        self.assertEqual(self.LOB.askDepth["100"], 10)
        self.assertEqual(self.LOB.getDepth(90, "bid"), -5)
        self.assertEqual(self.LOB.getDepth(100, "ask"), 10)
        self.assertEqual(self.LOB.lastPrice, 100)

    def test_place_MKT_order_partialFill(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.LOB.MKTorder(3)
        self.LOB.MKTorder(-6)

        self.assertEqual(self.LOB.bidDepth["90"], -2)
        self.assertEqual(self.LOB.askDepth["100"], 4)

    def test_place_MKT_order_fullFill(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.LOB.MKTorder(5)
        self.LOB.MKTorder(-10)

        self.assertEqual(self.LOB.bidDepth["90"], 0)
        self.assertEqual(self.LOB.askDepth["100"], 0)

    # should place remainder at best quote
    def test_place_MKT_order_overFill(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.LOB.MKTorder(21) # fills bid side, adds 16 to best ask price ["100"] = 26
        self.assertEqual(self.LOB.askDepth["100"], 26)
        self.LOB.PlaceOrder(90, -1) # add size to best bid so it doesn't return none
        self.LOB.MKTorder(-27) # fills ask side, adds 1 to best bid price ["90"] = -2
        self.assertEqual(self.LOB.bidDepth["90"], -2)

    def test_walk_book_MKT_order(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(89, -6)
        self.LOB.PlaceOrder(88, -9)

        self.LOB.PlaceOrder(100, 10)
        self.LOB.PlaceOrder(101, 5)
        self.LOB.PlaceOrder(102, 5)

        self.LOB.MKTorder(-21) # fills ask side, adds 1 to best bid price ["90"] = -6
        self.assertEqual(self.LOB.bidDepth["90"], -6) # now need 22 depth to overfill the bid side
        self.assertEqual(self.LOB.getDepth(100, "ask"), 0)
        self.assertEqual(self.LOB.getDepth(101, "ask"), 0)
        self.assertEqual(self.LOB.getDepth(102, "ask"), 0)

        self.LOB.PlaceOrder(100, 1) # add size to best ask so it doesn't return none
        self.LOB.MKTorder(22) # fills bid side, adds 1 to best ask price ["100"] = 2
        self.assertEqual(self.LOB.askDepth["100"], 2)
        self.assertEqual(self.LOB.getDepth(90, "ask"), 0)
        self.assertEqual(self.LOB.getDepth(89, "ask"), 0)
        self.assertEqual(self.LOB.getDepth(88, "ask"), 0)

    def test_walk_book_LMT_order(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(89, -6)
        self.LOB.PlaceOrder(88, -9)

        self.LOB.PlaceOrder(100, 10)
        self.LOB.PlaceOrder(101, 5)
        self.LOB.PlaceOrder(102, 5)

        # LMT orders
        self.LOB.PlaceOrder(103, -10) # fills at best ask
        self.assertEqual(self.LOB.askDepth["100"], 0)
        self.LOB.PlaceOrder(103, -10) # fills the other 2 asks
        self.assertEqual(self.LOB.askDepth["101"], 0)
        self.assertEqual(self.LOB.askDepth["102"], 0)

        self.LOB.PlaceOrder(87, 5) # fills at best bid
        self.assertEqual(self.LOB.bidDepth["90"], 0)
        self.LOB.PlaceOrder(87, 15)
        self.assertEqual(self.LOB.bidDepth["89"], 0)
        self.assertEqual(self.LOB.bidDepth["88"], 0)

    def test_last_price(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.assertEqual(self.LOB.lastPrice, 100)

        self.LOB.MKTorder(4)
        self.assertEqual(self.LOB.lastPrice, 90)

        self.LOB.MKTorder(-6)
        self.assertEqual(self.LOB.lastPrice, 100)

        self.LOB.PlaceOrder(89, -2)
        self.assertEqual(self.LOB.lastPrice, 89)

        self.LOB.PlaceOrder(101, 3)
        self.assertEqual(self.LOB.lastPrice, 101)

    def test_price_time_priority(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(90, -5)

        self.LOB.MKTorder(5)

        self.assertEqual(self.LOB.bidSet[0].size, 0)
        self.assertEqual(self.LOB.bidSet[1].size, -5)
        self.assertIsNone(self.LOB.findOrder(1))
        self.assertEqual(self.LOB.bidDepth["90"], -5)

    def test_best_quote(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.assertEqual(self.LOB.bidPrice, 90)
        self.assertEqual(self.LOB.askPrice, 100)
        self.assertEqual(self.LOB.bidSet[0].price, 90)
        self.assertEqual(self.LOB.askSet[0].price, 100)

        self.LOB.PlaceOrder(91, -5)
        self.LOB.PlaceOrder(99, 10)

        self.assertEqual(self.LOB.bidPrice, 91)
        self.assertEqual(self.LOB.askPrice, 99)
        self.assertEqual(self.LOB.bidSet[0].price, 91)
        self.assertEqual(self.LOB.askSet[0].price, 99)

    def test_spread(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.assertEqual(self.LOB.spread, 10)

        self.LOB.PlaceOrder(91, -5)
        self.LOB.PlaceOrder(99, 10)

        self.assertEqual(self.LOB.spread, 8)

    def test_mid_price(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.assertEqual(self.LOB.midPrice, 95)

        self.LOB.PlaceOrder(94, -5)
        self.LOB.PlaceOrder(98, 10)

        self.assertEqual(self.LOB.midPrice, 96)

    def test_cancel_order(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.LOB.CancelOrder(self.LOB.findOrder(1))
        self.assertIsNone(self.LOB.findOrder(1))
        self.assertEqual(self.LOB.bidDepth["90"], 0)
        self.assertEqual(self.LOB.getDepth(90, "bid"), 0)

        self.LOB.CancelOrder(self.LOB.findOrder(2))
        self.assertIsNone(self.LOB.findOrder(2))
        self.assertEqual(self.LOB.askDepth["100"], 0)
        self.assertEqual(self.LOB.getDepth(100, "ask"), 0)

    def test_get_relative_price(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(100, 10)

        self.assertEqual(self.LOB.getRelativePrice(0, "bid"), 90)
        self.assertEqual(self.LOB.getRelativePrice(1, "bid"), 89)
        self.assertEqual(self.LOB.getRelativePrice(2, "bid"), 88)

        self.assertEqual(self.LOB.getRelativePrice(0, "ask"), 100)
        self.assertEqual(self.LOB.getRelativePrice(1, "ask"), 101)
        self.assertEqual(self.LOB.getRelativePrice(2, "ask"), 102)

    def test_get_relative_depth(self):
        self.LOB.PlaceOrder(90, -5)
        self.LOB.PlaceOrder(89, -4)
        self.LOB.PlaceOrder(88, -3)
        self.LOB.PlaceOrder(100, 10)
        self.LOB.PlaceOrder(101, 9)
        self.LOB.PlaceOrder(102, 8)

        self.assertEqual(self.LOB.getRelativeDepth(0, "bid"), -5)
        self.assertEqual(self.LOB.getRelativeDepth(1, "bid"), -4)
        self.assertEqual(self.LOB.getRelativeDepth(2, "bid"), -3)

        self.assertEqual(self.LOB.getRelativeDepth(0, "ask"), 10)
        self.assertEqual(self.LOB.getRelativeDepth(1, "ask"), 9)
        self.assertEqual(self.LOB.getRelativeDepth(2, "ask"), 8)

if __name__ == '__main__':
    unittest.main()

    
