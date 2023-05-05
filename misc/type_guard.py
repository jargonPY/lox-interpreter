from typing import TypeVar, TypeGuard, Sequence

T = TypeVar("T")


def list_of_t(container: Sequence[T], types=str) -> TypeGuard[list[T]]:
    return all(isinstance(elem, types) for elem in container)


# container: Sequence[object] = ["jupiter", "mars"]
container: Sequence[object] = [4, 10]
if list_of_t(container):
    print(container[0].as_integer_ratio())


def is_operand_of_type(operand: T, expected_type=int) -> TypeGuard[int]:
    return isinstance(operand, expected_type)


def operands_of_type(operands: Sequence[T]) -> TypeGuard[list[int]]:
    return all(isinstance(operand, int) for operand in operands)


x: object = "4"
y: object = "10"
if is_operand_of_type(x):
    x.as_integer_ratio()
    print("HERE")

if operands_of_type([x, y]):
    print("THERE: ", x - y)

if is_operand_of_type(x) and is_operand_of_type(y):
    print("THERE: ", x - y)
