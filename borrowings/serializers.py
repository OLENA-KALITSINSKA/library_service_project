from rest_framework import serializers
from books.serializers import BookListSerializer
from borrowings.models import Borrowing
from users.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "user",
        )


class BorrowingListSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = BorrowingSerializer.Meta.fields


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookListSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = BorrowingSerializer.Meta.fields + ("actual_return_date",)
