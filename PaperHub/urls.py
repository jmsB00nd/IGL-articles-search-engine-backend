# urls.py

from django.urls import path
from .views import signup,update_user,add_moderator,update_moderator

urlpatterns = [
    path('user/signup/', signup, name='signup'),
    path('user/update-user/<int:user_id>/',update_user,name='update user'),
    path('moderator/add-moderator/',add_moderator,name="add moderator"),
    path('moderator/update-moderator/<int:user_id>/',update_moderator,name="update moderator")
]