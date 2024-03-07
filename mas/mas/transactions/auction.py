from .poly_line import PolyLine
from .point import Point


class Auction:
    def __init__(self, name) -> None:
        self.name = name

    def get_result(
        self, self_demand_curve: PolyLine, aggregate_bid_curve: PolyLine
    ) -> Point:
        try:
            return PolyLine.intersection(self_demand_curve, aggregate_bid_curve)
        except BaseException:
            return None
