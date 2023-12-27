from django.urls import path
from .views import logout_view


urlpatterns = [
     path('logout/',logout_view, name ='logout')
]