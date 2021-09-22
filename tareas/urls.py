from django.urls import path
from .views import recorrer_numero

urlpatterns = [
    #Urls 
   path('recorrer/', recorrer_numero, name='recorrer_numero')

]