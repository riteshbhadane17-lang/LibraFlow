"""Injects site-wide stats (used by the base template's navbar badge)."""


def site_stats(request):
    if not request.user.is_authenticated:
        return {}
    try:
        from apps.borrow.borrow_manager import BorrowManager
        from apps.borrow.notifications import unread_notifications
        return {
            "nav_overdue_count": BorrowManager.find_overdue().count(),
            "nav_unread_notifications": unread_notifications().count(),
        }
    except Exception:
        # MongoDB may not be reachable in some contexts (e.g. static admin
        # pages) -- fail soft rather than breaking every page render.
        return {}
