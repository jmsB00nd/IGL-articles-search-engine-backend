# urls.py

from django.urls import path
from .views import signup,update_user

urlpatterns = [
    path('user/signup/', signup, name='signup'),
    path('user/update-user/<int:user_id>/',update_user,name='update user')
]