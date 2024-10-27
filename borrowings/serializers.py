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
        read_only_fields = ("user",)

    def validate_book(self, value):
        if value.inventory < 1:
            raise serializers.ValidationError("No inventory available for this book.")
        return value

    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


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
