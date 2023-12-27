from django.urls import path

from . import feeds, views

urlpatterns = [
    path("theme.css", views.ThemeCSSView.as_view(), name="theme.css"),
    path("feed/rss", feeds.RSSFeed(), name="feed.rss"),
    path("feed/atom", feeds.AtomFeed(), name="feed.atom"),
    path("<str:date>/<int:pk>", views.IncidentDetailView.as_view(), name="detail"),
    path("", views.IndexView.as_view(), name="index"),
]
