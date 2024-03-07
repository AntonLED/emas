import numpy as np

from volttron.platform.vip.agent import Agent, Core, PubSub
from mas.transactions.topics import (
    DEMAND_BID_TOPIC,
    BID_OFFER_TOPIC,
    MARKET_CLEARING_TOPIC,
    MARKET_STATE_TOPIC,
    BIDDERS_INCOME,
)
from mas.transactions.bidder_solver import MPO_Solver as Solver
from mas.transactions.point import Point
from .agent_states import IDLE, INGAME


class BaseBidder(Agent):
    def __init__(self, name, rorm=0.0, price=1.0, power=0.0, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.state = INGAME
        self.rorm = rorm
        self.price = price
        # self.avail_power = power
        self.power = power
        # self.solver = Solver(rorm, price, power)
        self.curves = {}
        self.mpo_results = {}
        self.clear_values = {}
        # TODO: self.clear_values doesn't cleared in code below!

    @PubSub.subscribe("pubsub", MARKET_STATE_TOPIC)
    def market_state_callback(self, peer, sender, bus, topic, headers, message):
        if message == "bid-offer" and self.state == INGAME:
            self.bid_offer_trigger()
        elif message == "demand-bid" and self.state == INGAME:
            self.demand_bid_trigger()

    @PubSub.subscribe("pubsub", DEMAND_BID_TOPIC)
    def demand_bid_callback(self, peer, sender, bus, topic, headers, message):
        """
        Here we are recieve P-Q curve from asker (sender).
        Then, we should perform MPO optimization and send results to THIS asker.
        """
        if message["to"] == "all":
            self.curves[message["from"]] = message["data"]

    @PubSub.subscribe("pubsub", MARKET_CLEARING_TOPIC)
    def market_clearing_callback(self, peer, sender, bus, topic, headers, message):
        """
        Here we are recieve pair of values (power, corresponding price)
        that asker sender will buy from this bidder.
        """
        if message["to"] == self.name:
            self.clear_values[message["from"]] = message["data"]

    def bid_offer_trigger(self):
        tmp_curves = [curve for curve in self.curves.values()]
        results = self.perform_mpo(tmp_curves)
        for asker_name, asker_results in zip(list(self.curves.keys()), results):
            self.mpo_results[asker_name] = asker_results
            msg = {}
            msg["from"] = self.name
            msg["to"] = asker_name
            msg["data"] = asker_results
            self.vip.pubsub.publish(peer="pubsub", topic=BID_OFFER_TOPIC, message=msg)

    def demand_bid_trigger(self):
        self.apply_cycle()
        self.update_power()
        if self.clear_values:
            self.curves.clear()
            self.clear_values.clear()

    def perform_mpo(self, curves):
        """
        Here we are solving Markorvitz Portfolio Optimization problem and returns results
        """
        solver = Solver(power=self.power)

        new_curves = []
        for curve in curves:
            new_curve = []
            n = len(curve[0])
            for i in range(n):
                new_curve += [Point(curve[0][i], curve[1][i])]
            new_curves += [new_curve]

        return solver.solve(new_curves)

    def update_power(self):
        self.power = np.random.uniform(2.1 + 2.0, 8.0 + 2.0)
        print("\n")
        print(f"predicted power: {self.power}")
        print("\n")

    def apply_cycle(self):
        pass
