
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentification.urls')),
    path('elasticsearch/',include('elasticsearchApp.urls')),
    path('paperhub/',include('PaperHub.urls'))
]
