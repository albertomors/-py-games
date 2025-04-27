import random

# <--- methods --->

def remap(x,x1,x2,y1,y2):
    dx = x2-x1
    dy = y2-y1
    return y1 + (x-x1)*dy/dx

def clamped_remap(x,x1,x2,y1,y2):
    try:
        ymin = min(y1,y2)
        ymax = max(y1,y2)
        y = remap(x,x1,x2,y1,y2)
        return min(max(y,ymin),ymax)
    except ZeroDivisionError:
        return y1

def clamped_gaussian(a,b,mu):
    #3*sigma = half side = (b-a)/2
    sigma = (b-a)/2/3
    y = random.gauss(mu,sigma)
    clamped = min(max(a,y),b)
    return clamped