"""member_manager.py - CRUD + search for the `members` collection."""
from apps.members.models import MemberDocument
from core.exceptions import RecordNotFoundException
from core.validators import validate_member_id, validate_email, validate_phone


class MemberManager:

    @staticmethod
    def register_member(member_id, name, email, phone, membership_type="standard",
                         max_books=5) -> MemberDocument:
        validate_member_id(member_id)
        validate_email(email)
        validate_phone(phone)
        member = MemberDocument(
            member_id=member_id, name=name, email=email, phone=phone,
            membership_type=membership_type, max_books=max_books,
        )
        member.save()
        return member

    @staticmethod
    def update_member(member_id: str, **fields) -> MemberDocument:
        member = MemberManager.get_member(member_id)
        for key, value in fields.items():
            if hasattr(member, key) and value is not None:
                setattr(member, key, value)
        member.save()
        return member

    @staticmethod
    def delete_member(member_id: str) -> bool:
        member = MemberManager.get_member(member_id)
        member.delete()
        return True

    @staticmethod
    def get_member(member_id: str) -> MemberDocument:
        member = MemberDocument.objects(member_id=member_id).first()
        if not member:
            raise RecordNotFoundException(f"Member '{member_id}' not found")
        return member

    @staticmethod
    def search(query: str = ""):
        if not query:
            return MemberDocument.objects.all()
        from mongoengine.queryset.visitor import Q
        return MemberDocument.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query) | Q(member_id__icontains=query)
        )

    @staticmethod
    def list_members(page: int = 1, page_size: int = 20):
        skip = (page - 1) * page_size
        return MemberDocument.objects.order_by("name").skip(skip).limit(page_size)
