from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from apps.borrow.borrow_manager import BorrowManager
from apps.borrow.notifications import unread_notifications


def landing(request):
    return render(request, "dashboard/landing.html")


def about(request):
    return render(request, "dashboard/about.html")


def contact(request):
    return render(request, "dashboard/contact.html")


@login_required
@never_cache
def home(request):
    stats = BorrowManager.stats_summary()
    recent = BorrowManager.recently_borrowed(limit=8)
    notifications = unread_notifications(limit=5)
    most_borrowed = BorrowManager.most_borrowed_books(limit=5)
    return render(request, "dashboard/home.html", {
        "stats": stats,
        "recent": recent,
        "notifications": notifications,
        "most_borrowed": most_borrowed,
    })


@login_required
def reports(request):
    stats = BorrowManager.stats_summary()
    return render(request, "dashboard/reports.html", {"stats": stats})
