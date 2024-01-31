# urls.py

from django.urls import path
from .views import signup,update_user,add_moderator,update_moderator,add_to_favorite,delete_moderator,get_moderators

urlpatterns = [
    path('user/signup/', signup, name='signup'),
    path('user/update-user/<int:user_id>/',update_user,name='update user'),
    path('moderator/add-moderator/',add_moderator,name="add moderator"),
    path('moderator/update-moderator/<int:user_id>/',update_moderator,name="update moderator"),
    path('moderator/delete-moderator/<int:moderator_id>/',delete_moderator,name="delete moderator"),
    path('moderator/get_moderators/', get_moderators, name='get_moderators'),
    path('user/favorite/<int:user_id>/<int:article_id>/',add_to_favorite, name='add_to_favorite')
]