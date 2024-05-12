from django.contrib import admin
from django.urls import path, include
# from sentiment_analysis import views as sa_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("sentiment_analysis.urls")),
]
