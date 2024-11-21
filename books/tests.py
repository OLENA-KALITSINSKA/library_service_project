from decimal import Decimal

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book


BOOK_URL = reverse("book:book-list")


def sample_book(**params) -> Book:
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": Book.CoverChoices.HARD,
        "inventory": 5,
        "daily_fee": Decimal("1.50"),
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class BookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            password="user123",
            email="user@example.com",
            first_name="User",
            last_name="Test",
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_list_books(self):
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        url = reverse("book:book-detail", args=[self.book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book.title)

    def test_create_book_permission(self):
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": Book.CoverChoices.SOFT,
            "inventory": 3,
            "daily_fee": Decimal("2.50"),
        }

        response = self.client.post(BOOK_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_permission(self):
        url = reverse("book:book-detail", args=[self.book.id])
        data = {
            "title": "Updated Book Title",
            "author": self.book.author,
            "cover": self.book.cover,
            "inventory": self.book.inventory,
            "daily_fee": self.book.daily_fee,
        }

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_permission(self):
        url = reverse("book:book-detail", args=[self.book.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            password="user123",
            email="user@example.com",
            first_name="User",
            last_name="Test",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_create_book_permission(self):
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": Book.CoverChoices.SOFT,
            "inventory": 3,
            "daily_fee": Decimal("2.50"),
        }

        response = self.client.post(BOOK_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])

    def test_delete_book_permission(self):
        url = reverse("book:book-detail", args=[self.book.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_book_permission(self):
        url = reverse("book:book-detail", args=[self.book.id])
        data = {
            "title": "Updated Book Title",
            "author": self.book.author,
            "cover": self.book.cover,
            "inventory": self.book.inventory,
            "daily_fee": self.book.daily_fee,
        }

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], data["title"])
