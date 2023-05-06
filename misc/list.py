def print_hello():
    return [10, 20]


print(print_hello()[0])

print([print_hello][0]())

x = [10]
x[0] = 100
