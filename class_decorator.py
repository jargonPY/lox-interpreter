from typing import Callable


def print_arguments_decorator(func: Callable):
    def wrapper(*args, **kwargs):
        print("Arguments:", args, kwargs)
        return func(*args, **kwargs)

    return wrapper


def my_decorator(cls):
    class NewClass:
        def __init__(self, *args, **kwargs):
            self.obj = cls(*args, **kwargs)

        def __getattribute__(self, name):
            attr = self.obj.__getattribute__(name)
            if callable(attr):
                attr = print_arguments_decorator(attr)
            return attr

    return NewClass


@my_decorator
class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass
