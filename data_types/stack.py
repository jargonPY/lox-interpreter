from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> Optional[T]:
        if not self.is_empty():
            return self.items.pop()

        return None

    def peek(self) -> Optional[T]:
        if not self.is_empty():
            return self.items[-1]

        return None

    def get(self, index: int) -> Optional[T]:
        if not self.is_empty():
            return self.items[index]

        return None

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def size(self) -> int:
        return len(self.items)
