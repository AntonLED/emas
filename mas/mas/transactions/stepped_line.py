from .point import Point


class SteppedLine:
    def __init__(self, points=[]):
        self.points = points

    def add_point(self, point: Point):
        self.points.append(point)

    def add_points(self, points: list[Point]):
        for point in points:
            self.add_point(point)

    def is_contains_points(self):
        return bool(self.points)

    @staticmethod
    def __area(a: Point, b: Point, c: Point):
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

    @staticmethod
    def __intersect_1(a: float, b: float, c: float, d: float):
        if a > b:
            a, b = b, a
        if c > d:
            c, d = d, c
        return max(a, c) <= min(b, d)

    @staticmethod
    def __intersect(a, b, c, d):
        return (
            SteppedLine.__intersect_1(a.x, b.x, c.x, d.x)
            and SteppedLine.__intersect_1(a.y, b.y, c.y, d.y)
            and SteppedLine.__area(a, b, c) * SteppedLine.__area(a, b, d) <= 0
            and SteppedLine.__area(c, d, a) * SteppedLine.__area(c, d, b) <= 0
        )

    @staticmethod
    def intersect(curve1, curve2):
        for i in range(len(curve1.points) - 1):
            for j in range(len(curve2.points) - 1):
                a = curve1.points[i]
                b = curve1.points[i + 1]
                c = curve2.points[j]
                d = curve2.points[j + 1]
                if c.x > b.x:
                    break
                if SteppedLine.__intersect(a, b, c, d):
                    if a.y == b.y == c.y == d.y:
                        return Point(min(b.x, d.x), a.y)
                    elif a.x == b.x == c.x == d.x:
                        return Point(a.x, min(a.y, d.y))
                    elif a.y == b.y:
                        return Point(c.x, b.y)
                    else:
                        return Point(a.x, c.y)
        return Point(None, None)
