from django.urls import path
from apps.members import views

app_name = "members"

urlpatterns = [
    path("", views.member_list, name="list"),
    path("register/", views.member_register, name="register"),
    path("<str:member_id>/", views.member_detail, name="detail"),
    path("<str:member_id>/delete/", views.member_delete, name="delete"),
]
