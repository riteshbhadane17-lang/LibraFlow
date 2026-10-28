from django.apps import AppConfig
import os


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    label = "dashboard"

    def ready(self):
        # Avoid starting the thread twice under the dev-server autoreloader,
        # and never start it during `manage.py migrate`/`makemigrations` etc.
        if os.environ.get("RUN_MAIN") != "true":
            return
        from django.conf import settings
        from core.threading_jobs import start_overdue_checker
        start_overdue_checker(
            interval_hours=settings.LIBRAFLOW["OVERDUE_CHECK_INTERVAL_HOURS"],
            backup_dir=settings.LIBRAFLOW["BACKUP_DIR"],
        )
