import math


def euclid(a, b):
    return math.sqrt(a**2.0, b**2.0)

def euclid(x0,y0,x1,y1):
    return euclid(x1-x0, y1-y0)