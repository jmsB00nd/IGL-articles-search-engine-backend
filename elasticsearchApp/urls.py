from django.urls import  path
from .views import download_pdf



urlpatterns = [
    path("<path:url>/", download_pdf, name="download_pdf"),
]