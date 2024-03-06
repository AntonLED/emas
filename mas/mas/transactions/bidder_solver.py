import cvxpy as cp
import numpy as np
from .point import Point

# curve: list of Points
# point: Point(q, p), self.x = q, self.y = p


class MPO_Solver:
    def __init__(self, rorm=None, price=None, power=None) -> None:
        self.rorm = rorm
        self.price = price
        self.power = power

    @staticmethod
    def _extract_quantities(curve: list[Point]) -> list[float]:
        curve_quantities = []
        for point in curve:
            curve_quantities += [point.x]
        return curve_quantities

    @staticmethod
    def _extract_prices(curve: list[Point]) -> list[float]:
        curve_prices = []
        for point in curve:
            curve_prices += [point.y]
        return curve_prices

    @staticmethod
    def _extract_direct_prices(curves: list[list[Point]]) -> list[float]:
        assets_prices = []
        for curve in curves:
            for point in curve:
                assets_prices += [point.y]
        return assets_prices

    @staticmethod
    def _extract_direct_quantities(curves: list[list[Point]]) -> list[float]:
        assets_quantities = []
        for curve in curves:
            for point in curve:
                assets_quantities += [point.x]
        return assets_quantities

    # FIXME: fix this
    def _extract_required_power(curve: list[Point]) -> float:
        for point in curve:
            if point.y == 0.0:
                return point.x

    # FIXME: fix this
    def _extract_direct_required_power(curves: list[list[Point]]) -> list[Point]:
        return [MPO_Solver._extract_required_power(curve) for curve in curves]

    def solve(
        self, curves: list[list[Point]], samples: int = 300
    ) -> list[list[float, float]]:
        assets_cnt = len(curves)
        ###
        prices = []
        for curve in curves:
            prices += [np.max(MPO_Solver._extract_prices(curve)) * 0.95]
        ###
        cost = 1.0
        self.power -= 2.0
        # points' data normalization
        for i in range(len(curves)):
            for point in curves[i]:
                point.x /= self.power
                point.y /= cost

        # TODO: optimize it with numpy
        max_q = np.max([q for q in MPO_Solver._extract_direct_quantities(curves)])
        general_sampled_qs = np.linspace(0, max_q, samples)
        assets_sampled_ps = []
        for curve in curves:
            asset_sampled_ps = []
            for q in general_sampled_qs:
                for i in range(len(curve) - 1):
                    if (q >= curve[i].x) and (q <= curve[i + 1].x):
                        asset_sampled_ps += [curve[i].y]
                        break
                if q > curve[-1].x:
                    asset_sampled_ps += [0.0]
            assets_sampled_ps += [asset_sampled_ps]

        assets_sampled_rs = np.array(list(map(np.array, assets_sampled_ps))) - 1.0

        mid_assets_rs = list(map(np.mean, assets_sampled_rs))

        # sigma = np.cov(assets_sampled_rs - mid_assets_rs.reshape((assets_cnt, 1)))

        available_power = 1.0
        w = [0.0, 0.0]
        _mid_assets_rs = list(enumerate(mid_assets_rs))
        for _ in range(assets_cnt):
            best_return = max(_mid_assets_rs, key=lambda el: el[1])
            best_return_id, _ = best_return
            _mid_assets_rs.remove(best_return)
            required_power = MPO_Solver._extract_required_power(curves[best_return_id])
            print("\n\n")
            print(required_power * self.power, best_return_id, sep="    ")
            print(available_power * self.power)
            print("\n\n")
            if available_power - required_power > 0.0:
                w[best_return_id] = required_power
            available_power -= required_power

        #         w = cp.Variable(assets_cnt)
        #         gamma = cp.Parameter(nonneg=True)
        #         gamma.value = 0.5
        #         outcome = assets_outcome.T @ w
        #         powers = MPO_Solver._extract_direct_required_power(curves)

        #         print(outcome)

        # # outcome * 0.00000001
        #         risk = cp.quad_form(w, sigma)
        #         prob = cp.Problem(cp.Maximize(outcome),
        #                           [cp.sum(w) == 1, w >= 0])
        #         prob.solve(solver=cp.ECOS)

        print("\n\n\n")
        print([round(weight * self.power, 2) for weight in w])
        print("\n\n\n")

        return [(weight * self.power, cost) for weight in w]
