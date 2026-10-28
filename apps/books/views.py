"""Class/function-based views for the book catalog (Unit 5 web pages)."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from apps.books.book_manager import BookManager
from apps.books.forms import BookForm, BookSearchForm
from core.exceptions import LibraFlowException, RecordNotFoundException


def book_catalog(request):
    form = BookSearchForm(request.GET or None)
    books = BookManager.search()
    if form.is_valid():
        books = BookManager.search(
            query=form.cleaned_data.get("query", ""),
            category=form.cleaned_data.get("category", ""),
            available_only=form.cleaned_data.get("available_only", False),
        )
    paginator = Paginator(list(books), 9)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    return render(request, "books/catalog.html", {
        "form": form, "page_obj": page_obj, "categories": BookManager.categories(),
    })


def book_detail(request, book_id):
    try:
        book = BookManager.get_book(book_id)
    except RecordNotFoundException:
        messages.error(request, "Book not found.")
        return redirect("books:catalog")
    return render(request, "books/detail.html", {"book": book})


@login_required
def book_add(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            try:
                BookManager.add_book(**form.cleaned_data)
                messages.success(request, "Book added successfully.")
                return redirect("books:catalog")
            except LibraFlowException as exc:
                messages.error(request, str(exc))
    else:
        form = BookForm()
    return render(request, "books/form.html", {"form": form, "mode": "Add"})


@login_required
def book_edit(request, book_id):
    book = BookManager.get_book(book_id)
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                data.pop("book_id")  # book_id is immutable once created
                BookManager.update_book(book_id, **data)
                messages.success(request, "Book updated successfully.")
                return redirect("books:detail", book_id=book_id)
            except LibraFlowException as exc:
                messages.error(request, str(exc))
    else:
        form = BookForm(initial=book.to_dict())
    return render(request, "books/form.html", {"form": form, "mode": "Edit", "book": book})


@login_required
def book_delete(request, book_id):
    if request.method == "POST":
        BookManager.delete_book(book_id)
        messages.success(request, "Book deleted.")
    return redirect("books:catalog")
