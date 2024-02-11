from django.urls import path, register_converter

from . import feeds, views


class DateConverter:
    regex = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(DateConverter, "date")

urlpatterns = [
    path("feed/rss", feeds.RSSFeed(), name="feed.rss"),
    path("feed/atom", feeds.AtomFeed(), name="feed.atom"),
    path("<date:date>/<int:pk>", views.IncidentDetailView.as_view(), name="detail"),
    path("<date:date>/<int:pk>", views.IncidentDetailView.as_view(), name="detail"),
    path("<date:date>", views.DayView.as_view(), name="day"),
    path("history", views.HistoryView.as_view(), name="history"),
    path(
        "unsubscribe/done", views.UnsubscribeDoneView.as_view(), name="unsubscribe.done"
    ),
    path(
        "unsubscribe/<str:token>", views.UnsubscribeView.as_view(), name="unsubscribe"
    ),
    path("", views.IndexView.as_view(), name="index"),
]
