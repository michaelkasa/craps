class Bacon:
    def __init__(self,f):
        self.f = f
    secret_value = 'secrets!!!!!!'

def g():
    print('Say hi!')

def h(self):
    print(self.secret_value)

b = Bacon(g)
b.f()

bprime = Bacon(h)
bprime.f(bprime)
