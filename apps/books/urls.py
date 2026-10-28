from django.urls import path
from apps.books import views

app_name = "books"

urlpatterns = [
    path("", views.book_catalog, name="catalog"),
    path("add/", views.book_add, name="add"),
    path("<str:book_id>/", views.book_detail, name="detail"),
    path("<str:book_id>/edit/", views.book_edit, name="edit"),
    path("<str:book_id>/delete/", views.book_delete, name="delete"),
]
