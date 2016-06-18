__author__ = 'hcy'

def enum(**enums):
    return type('Enum', (), enums)

Numbers = enum(ONE="aa",TWO=2,THREE='three')

N ={
    "key1":"valu1",
    "key2":"value2"
}

# def send(a):
#


if __name__ == '__main__':
  print Numbers.ONE
