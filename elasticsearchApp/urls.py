from django.urls import  path
from .views import add_article,download_pdf



urlpatterns = [
    path("add_article/",add_article,name='add_article'),
    path("<path:url>/", download_pdf, name="download_pdf"),
]