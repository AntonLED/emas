from mas.transactions.stepped_line import SteppedLine
from mas.transactions.point import Point


points1 = [Point(0, 4), Point(3, 4), Point(3, 3), Point(5, 3), Point(5, 1)]
points2 = [
    Point(0, 1),
    Point(2, 1),
    Point(2, 2),
    Point(3, 2),
    Point(3, 3),
    Point(4, 3),
    Point(4, 4),
]

curve1 = SteppedLine()
curve2 = SteppedLine()

assert not curve1.is_contains_points()
assert not curve2.is_contains_points()

curve1.add_points(points1)
curve2.add_points(points2)

assert curve1.is_contains_points()
assert curve2.is_contains_points()

p = SteppedLine.intersect(curve1, curve2)

assert p.x == 3
assert p.y == 3
