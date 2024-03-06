import numpy as np
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, PubSub
from mas.transactions.topics import (
    DEMAND_BID_TOPIC,
    BID_OFFER_TOPIC,
    MARKET_CLEARING_TOPIC,
    MARKET_STATE_TOPIC,
    MARKET_AGGREGATE,
)
from mas.transactions.auction import Auction
from mas.transactions.poly_line import PolyLine
from mas.transactions.point import Point
from .agent_states import IDLE, INGAME


class BaseAsker(Agent):
    def __init__(self, name="AskerAgent", **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.state = INGAME
        self.auction = Auction(name)
        self.curve = PolyLine()
        self.bid_offer_results = {}
        self.cur_power = None
        self.cur_price = None

    @PubSub.subscribe("pubsub", BID_OFFER_TOPIC)
    def bid_offer_callback(self, peer, sender, bus, topic, headers, message):
        """
        triggered every time when recieve offer_messages from each bidders
        """
        if message["to"] == self.name:
            self.bid_offer_results[message["from"]] = [
                message["data"][0],
                message["data"][1],
            ]

    @PubSub.subscribe("pubsub", MARKET_STATE_TOPIC)
    def market_state_callback(self, peer, sender, bus, topic, headers, message):
        """
        Triggered every time when recieve market_state_message from scheduler.
        """
        if message == "demand-bid":
            # here begin the trading cycle
            self.demand_bid_trigger()
        elif message == "market-clearing" and self.state == INGAME:
            # here we are sending market clearing messages
            self.market_clearing_trigger()

    def demand_bid_trigger(self):
        self.apply_clearing()

        self.update_curve()
        msg = {}
        msg["from"] = self.name
        msg["to"] = "all"
        msg["data"] = self.curve.vectorize()
        self.vip.pubsub.publish(peer="pubusb", topic=DEMAND_BID_TOPIC, message=msg)

    def market_clearing_trigger(self):
        bidder_curves = []
        for data in self.bid_offer_results.values():
            bidder_curve = PolyLine()
            bidder_curve.add(Point(0.0, data[1]))
            bidder_curve.add(Point(data[0], data[1]))
            bidder_curves.append(bidder_curve)
        aggregate_bid_curve = PolyLine.combine_segments(bidder_curves)
        clear_point = self.auction.get_result(self.curve, aggregate_bid_curve)

        print("\n")
        print(f"Asker: {self.name}, clear_point: {clear_point}")
        print("\n")

        msg = {}
        msg["from"] = self.name
        msg["to"] = "all"
        msg["data"] = aggregate_bid_curve.vectorize()
        self.vip.pubsub.publish(peer="pubsub", topic=MARKET_AGGREGATE, message=msg)

        if clear_point.x is None or clear_point.y is None:
            clear_point = Point(-1.0, -1.0)

        for bidder_name in self.bid_offer_results.keys():
            msg = {}
            msg["from"] = self.name
            msg["to"] = bidder_name
            msg["data"] = [clear_point.x, clear_point.y]
            self.vip.pubsub.publish(
                peer="pubusb", topic=MARKET_CLEARING_TOPIC, message=msg
            )
        self.bid_offer_results.clear()
        ###
        self.cur_power = clear_point.x
        self.cur_price = clear_point.y
        if not bidder_curves:
            self.cur_power = None
            self.cur_price = None

    def get_random_points(self):
        points = []
        size = np.random.randint(7, 10)
        qs = sorted(np.random.uniform(0.1, 8.0, size))
        ps = sorted(np.random.uniform(0.1, 8.0, size), reverse=True)
        points.append(Point(0.0, ps[0]))
        for i in range(0, size - 2):
            points.append(Point(qs[i], ps[i]))
            points.append(Point(qs[i] * 1.0001, ps[i + 1]))
        points.append(Point(qs[size - 3] * 1.0001, 0.0))
        return points

    def update_curve(self):
        points = self.get_random_points()
        if self.curve.points:
            self.curve.clear()
        for point in points:
            self.curve.add(point)

    def apply_clearing(self):
        pass
