from django.urls import  path
from .views import download_pdf,download_pdf_drive,get_data_elasticsearch,get_articles_mod,delete_article,search_articles,get_article_by_id,get_favourite,update_article,get_articles_mod_by_id



urlpatterns = [
    path("url/<path:url>/", download_pdf, name="download_pdf"),
    path("drive/<str:id>/", download_pdf_drive, name="download_pdf_drive"),
    path("get_data/",get_data_elasticsearch, name="get_data"),
    path("get_articles_mod/",get_articles_mod, name="get_articles_mod"),
    path("get_articles_mod_id/<int:article_id>/",get_articles_mod_by_id, name="get_articles_mod_id"),
    path("get_article_id/<int:article_id>/",get_article_by_id, name="get_articles_id"),
    path("update_article/<int:article_id>/",update_article, name="update_article"),
    path("delete_article/<int:article_id>/",delete_article, name="delete_article"),
    path("get_favorites/<int:user_id>/",get_favourite, name="get-favourite_article"),
    path("search/<str:search_query>/",search_articles, name="search_article"),
]