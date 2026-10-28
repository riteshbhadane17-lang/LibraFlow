from django.urls import path
from apps.borrow import views

app_name = "borrow"

urlpatterns = [
    path("new/", views.borrow_book, name="borrow"),
    path("return/", views.return_book, name="return"),
    path("history/", views.borrow_history, name="history"),
    path("overdue/", views.overdue_books, name="overdue"),
    path("history/export/csv/", views.export_history_csv, name="export_csv"),
]
