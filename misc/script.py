class A:
    def __init__(self) -> None:
        self.x = "10"

    def __eq__(self, other):
        if isinstance(other, A):
            return self.x == other.x
        return False


x = A()
y = A()

print(x == y)
