from django.urls import  path
from .views import download_pdf,download_pdf_drive,get_data_elasticsearch



urlpatterns = [
    path("url/<path:url>/", download_pdf, name="download_pdf"),
    path("drive/<str:id>/", download_pdf_drive, name="download_pdf_drive"),
    path("get_data/",get_data_elasticsearch, name="get_data")
]