from django.urls import path
from apps.api import views

app_name = "api"

urlpatterns = [
    path("books/", views.BookListCreateAPIView.as_view(), name="book-list"),
    path("books/<str:book_id>/", views.BookDetailAPIView.as_view(), name="book-detail"),
    path("members/", views.MemberListAPIView.as_view(), name="member-list"),
    path("borrow/", views.BorrowListCreateAPIView.as_view(), name="borrow-list"),
    path("return/", views.ReturnAPIView.as_view(), name="return"),
    path("overdue/", views.OverdueAPIView.as_view(), name="overdue"),
]
