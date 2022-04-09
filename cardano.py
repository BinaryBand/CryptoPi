from curve import invert


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def main() -> None:
    P: Point = Point(1, 8 ** 0.5)
    Q: Point = Point(3, 34 ** 0.5)

    lam: float = (Q.y - P.y) / (Q.x - P.x)
    beta: float = P.y - lam * P.x

    curve_a: float = 0
    curve_b: float = 7

    a: float = 1
    b: float = -(lam ** 2)
    c: float = curve_a - 2 * lam * beta
    d: float = curve_b - beta ** 2

    x1: float = (-b / a) - Q.x - P.x            # p + q + r     = -b / a
    x2: int = (c / a - P.x * Q.x) / (Q.x + P.x) # pq + qr + rp  = c / a
    x3: int = -d / (P.x * Q.x * a)              # pqr           = -d / a
    
    y: int = (lam * (x1 - Q.x) + Q.y)

    print('x=', x1, x2, x3)
    print('y=', y)


if __name__ == '__main__':
    main()