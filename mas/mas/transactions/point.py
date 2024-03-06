class Point:
    def __init__(self, quantity: float, price: float):
        self.x = quantity
        self.y = price

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
