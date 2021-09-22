from django.shortcuts import render
from .tasks import recorrer, add, mul,xsum
# Create your views here.



def recorrer_numero(request):
    resultado= recorrer.delay(10)
    add.delay(2,8)
    mul.delay(3,5)
    xsum.delay([3,4,5,6])
    add.delay(2,1)
    mul.delay(1,1)
    
