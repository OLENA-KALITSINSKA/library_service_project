from rest_framework import viewsets

from books.models import Book
from books.serializers import (
    BookDetailSerializer,
    BookSerializer,
    BookListSerializer
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        elif self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer
