from django.urls import path
from . import views

urlpatterns = [
    path("", views.form, name="home"),
    path("tweet_sentiment/", views.analyze, name="analyze"),
    path("gs/", views.getTweet, name="getScores"),
]