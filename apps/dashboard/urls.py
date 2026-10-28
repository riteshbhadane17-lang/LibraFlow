from django.urls import path
from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("dashboard/", views.home, name="home"),
    path("reports/", views.reports, name="reports"),
]
