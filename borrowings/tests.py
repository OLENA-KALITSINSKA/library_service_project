from django.contrib.auth import get_user_model
from django.test import TestCase
from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from borrowings.models import Borrowing
from books.models import Book

BORROWING_URL = reverse("borrowing:borrowing-list")


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_flight_auth_required(self):
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BorrowingViewSetTestCase(APITestCase):
    @staticmethod
    def create_book(title="Test Book", inventory=5, daily_fee=1.99):
        return Book.objects.create(
            title=title, inventory=inventory, daily_fee=daily_fee
        )

    @staticmethod
    def create_borrowing(
        user, book, borrow_date=None, expected_return_date=None, actual_return_date=None
    ):
        return Borrowing.objects.create(
            user=user,
            book=book,
            borrow_date=borrow_date or date.today(),
            expected_return_date=expected_return_date or date.today(),
            actual_return_date=actual_return_date,
        )

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            password="user123",
            email="user@example.com",
            first_name="User",
            last_name="Test",
        )

        self.book = self.create_book()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_borrowings(self):
        self.create_borrowing(self.user, self.book)
        self.create_borrowing(self.user, self.book)

        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_borrowing(self):
        data = {
            "borrow_date": date.today(),
            "expected_return_date": date.today(),
            "book": self.book.id,
        }
        response = self.client.post(BORROWING_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

    def test_create_borrowing_no_inventory(self):
        self.book.inventory = 0
        self.book.save()

        data = {
            "borrow_date": date.today(),
            "expected_return_date": date.today(),
            "book": self.book.id,
        }
        response = self.client.post(BORROWING_URL, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No inventory available for this book.", str(response.data))

    def test_return_book_success(self):
        borrowing = self.create_borrowing(self.user, self.book)

        url = reverse("borrowings:borrowing-return-book", kwargs={"pk": borrowing.id})
        response = self.client.put(url, {"actual_return_date": date.today()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()
        self.assertEqual(borrowing.actual_return_date, date.today())
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

    def test_return_book_already_returned(self):
        borrowing = self.create_borrowing(
            self.user, self.book, actual_return_date=date.today()
        )

        url = reverse("borrowings:borrowing-return-book", kwargs={"pk": borrowing.id})
        response = self.client.put(url, {"actual_return_date": date.today()})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This book has already been returned.", str(response.data))

    def test_list_borrowings_by_non_staff_user(self):
        another_user = get_user_model().objects.create_user(
            password="another_user123",
            email="anotheruser@example.com",
            first_name="Another_User",
            last_name="Test",
        )
        self.create_borrowing(self.user, self.book)
        self.create_borrowing(another_user, self.book)

        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_queryset_with_is_active_filter_true(self):
        self.create_borrowing(self.user, self.book)
        self.create_borrowing(self.user, self.book)

        response = self.client.get(BORROWING_URL, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class AdminBorrowingsApiTests(TestCase):
    @staticmethod
    def create_book(title="Test Book", inventory=5, daily_fee=1.99):
        return Book.objects.create(
            title=title, inventory=inventory, daily_fee=daily_fee
        )

    @staticmethod
    def create_borrowing(
        user, book, borrow_date=None, expected_return_date=None, actual_return_date=None
    ):
        return Borrowing.objects.create(
            user=user,
            book=book,
            borrow_date=borrow_date or date.today(),
            expected_return_date=expected_return_date or date.today(),
            actual_return_date=actual_return_date,
        )

    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            password="user123",
            email="staff@example.com",
            first_name="Staff",
            last_name="User",
            is_staff=True,
        )
        self.user = get_user_model().objects.create_user(
            password="user123",
            email="user@example.com",
            first_name="User",
            last_name="Test",
        )
        self.book = self.create_book()
        self.client = APIClient()
        self.client.force_authenticate(self.staff_user)

    def test_list_borrowings_by_staff_user(self):
        self.create_borrowing(self.user, self.book)
        self.create_borrowing(self.staff_user, self.book)

        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_queryset_for_staff_user_with_user_id_filter(self):
        self.create_borrowing(self.user, self.book)
        self.create_borrowing(self.user, self.book, actual_return_date=date.today())

        response = self.client.get(BORROWING_URL, {"user_id": self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
