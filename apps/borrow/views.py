from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from apps.borrow.borrow_manager import BorrowManager
from apps.borrow.forms import BorrowForm, ReturnForm, ReportFilterForm
from apps.borrow.backup_manager import export_borrow_history_csv
from core.exceptions import LibraFlowException


@login_required
def borrow_book(request):
    if request.method == "POST":
        form = BorrowForm(request.POST)
        if form.is_valid():
            try:
                record = BorrowManager.borrow_book(**form.cleaned_data)
                messages.success(request, f"Book '{record.book_id}' borrowed. Due {record.due_date:%Y-%m-%d}.")
                return redirect("dashboard:home")
            except LibraFlowException as exc:
                messages.error(request, str(exc))
    else:
        form = BorrowForm()
    return render(request, "borrow/borrow_form.html", {"form": form})


@login_required
def return_book(request):
    if request.method == "POST":
        form = ReturnForm(request.POST)
        if form.is_valid():
            try:
                record = BorrowManager.return_book(**form.cleaned_data)
                if record.fine_amount:
                    messages.warning(request, f"Book returned. Fine incurred: {record.fine_amount}.")
                else:
                    messages.success(request, "Book returned on time. Thank you!")
                return redirect("dashboard:home")
            except LibraFlowException as exc:
                messages.error(request, str(exc))
    else:
        form = ReturnForm()
    return render(request, "borrow/return_form.html", {"form": form})


@login_required
def borrow_history(request):
    form = ReportFilterForm(request.GET or None)
    records = BorrowManager.borrow_history()
    if form.is_valid():
        member_id = form.cleaned_data.get("member_id")
        status = form.cleaned_data.get("status")
        if member_id:
            records = records.filter(member_id=member_id)
        if status:
            records = records.filter(status=status)
    return render(request, "borrow/history.html", {"records": records, "form": form})


@login_required
def overdue_books(request):
    records = BorrowManager.find_overdue()
    return render(request, "borrow/overdue.html", {"records": records})


@login_required
def export_history_csv(request):
    records = BorrowManager.borrow_history()
    path = export_borrow_history_csv(records)
    with open(path, "rb") as f:
        response = HttpResponse(f.read(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{path.name}"'
        return response
