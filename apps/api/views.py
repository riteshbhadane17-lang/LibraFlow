"""
DRF API views implementing the endpoints required by the spec:

GET/POST/PUT/DELETE /api/books/
GET                 /api/members/
GET/POST            /api/borrow/
POST                /api/return/
GET                 /api/overdue/
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from apps.books.book_manager import BookManager
from apps.members.member_manager import MemberManager
from apps.borrow.borrow_manager import BorrowManager
from apps.api.serializers import BookSerializer, MemberSerializer, BorrowRecordSerializer
from core.exceptions import LibraFlowException, RecordNotFoundException


class BookListCreateAPIView(APIView):
    """GET /api/books/  |  POST /api/books/"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        query = request.query_params.get("q", "")
        category = request.query_params.get("category", "")
        books = BookManager.search(query=query, category=category)
        data = [BookSerializer(b.to_dict()).data for b in books]
        return Response(data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            book = BookManager.add_book(**serializer.validated_data)
            return Response(BookSerializer(book.to_dict()).data, status=status.HTTP_201_CREATED)
        except LibraFlowException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class BookDetailAPIView(APIView):
    """GET / PUT / DELETE  /api/books/<book_id>/"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, book_id):
        try:
            book = BookManager.get_book(book_id)
        except RecordNotFoundException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(BookSerializer(book.to_dict()).data)

    def put(self, request, book_id):
        try:
            book = BookManager.update_book(book_id, **request.data)
            return Response(BookSerializer(book.to_dict()).data)
        except RecordNotFoundException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except LibraFlowException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, book_id):
        try:
            BookManager.delete_book(book_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except RecordNotFoundException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)


class MemberListAPIView(APIView):
    """GET /api/members/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        members = MemberManager.search(request.query_params.get("q", ""))
        data = [MemberSerializer(m.to_dict()).data for m in members]
        return Response(data)


class BorrowListCreateAPIView(APIView):
    """GET /api/borrow/  |  POST /api/borrow/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        member_id = request.query_params.get("member_id")
        book_id = request.query_params.get("book_id")
        records = BorrowManager.borrow_history(member_id=member_id, book_id=book_id)
        data = [BorrowRecordSerializer(r.to_dict()).data for r in records]
        return Response(data)

    def post(self, request):
        try:
            record = BorrowManager.borrow_book(
                member_id=request.data.get("member_id"),
                book_id=request.data.get("book_id"),
            )
            return Response(BorrowRecordSerializer(record.to_dict()).data, status=status.HTTP_201_CREATED)
        except LibraFlowException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class ReturnAPIView(APIView):
    """POST /api/return/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            record = BorrowManager.return_book(
                member_id=request.data.get("member_id"),
                book_id=request.data.get("book_id"),
            )
            return Response(BorrowRecordSerializer(record.to_dict()).data)
        except LibraFlowException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class OverdueAPIView(APIView):
    """GET /api/overdue/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        records = BorrowManager.find_overdue()
        data = [BorrowRecordSerializer(r.to_dict()).data for r in records]
        return Response(data)
