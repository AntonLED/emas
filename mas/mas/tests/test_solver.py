import numpy as np
from mas.transactions.bidder_solver import MPO_Solver
from mas.transactions.point import Point
import copy


# curves = [
#     [Point(0, 8), Point(2, 8), Point(2, 2), Point(7, 2)],
#     [Point(0, 7), Point(1, 7), Point(1, 2), Point(4, 2), Point(4, 0), Point(10, 0)],
#     [Point(0, 6), Point(2, 6)]
# ]

# curves = [
#     [Point(0, 7), Point(3000, 7), Point(3000, 0), Point(5000, 0)],
#     [Point(0, 5), Point(1000, 5), Point(1000, 0), Point(5000, 0)],
#     [Point(0, 3), Point(200, 3), Point(200, 0), Point(5000, 0)]
# ]

curves = [
    [
        Point(0, 0),
        Point(3, 0),
        Point(3, 2),
        Point(3 * (1 + 0.01), 2),
        Point(3 * (1 + 0.01), 0),
    ],
    [
        Point(0, 0),
        Point(0.5, 0),
        Point(0.5, 5),
        Point(0.5 * (1 + 0.01), 5),
        Point(0.5 * (1 + 0.01), 0),
    ],
]

curves1 = [
    [Point(0, 3), Point(3, 3), Point(3, 0)],
    [Point(0, 10), Point(1, 10), Point(1, 0)],
]

# xs = []
# ys = []
# for curve in curves:
#     for p in curve:
#         xs.append(p.x)
#         ys.append(p.y)

# plt.scatter(xs, ys)

for power in np.linspace(2.3, 10.0, 30):
    slv = MPO_Solver(rorm=-10, price=1, power=power - 2.0)

    slv.solve(curves=copy.deepcopy(curves1))

# slv = MPO_Solver(rorm=-10, price=1, power=5.0)
# slv.solve(curves=copy.deepcopy(curves1))
