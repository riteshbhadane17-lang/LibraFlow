"""
BookDocument is a MongoEngine document, not a Django ORM model, so it
can't be registered with django.contrib.admin directly. This lightweight
custom admin view reuses BookManager and renders through the normal
template system instead of the Django admin site.
See apps/dashboard/views.py -> admin_books() for the management UI.
"""
