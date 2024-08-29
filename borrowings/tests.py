from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from borrowings.models import Borrowing
from books.models import Book
from borrowings.serializers import BorrowingSerializer

BORROWING_URL = reverse("borrowings:borrowing-list-create")


def detail_url(borrowing_id):
    """Return borrowing detail URL"""
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id):
    """Return borrowing return URL"""
    return reverse("borrowings:borrowing-return", args=[borrowing_id])


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Sample Author",
        "cover": "HARD",
        "inventory": 10,
        "daily_fee": 1.50,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_borrowing(user, book, **params):
    defaults = {
        "borrow_date": date.today(),
        "expected_return_date": date.today() + timedelta(days=7),
        "book": book,
        "user": user,
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingApiTests(TestCase):
    """Test the borrowings API (unauthenticated)"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    """Test the borrowings API (authenticated)"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_borrowings(self):
        """Test retrieving a list of borrowings"""
        book = sample_book()
        sample_borrowing(user=self.user, book=book)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        """Test creating a borrowing"""
        book = sample_book()
        payload = {
            "book": book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }
        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.get(id=res.data["id"])
        self.assertEqual(borrowing.book.id, payload["book"])
        self.assertEqual(borrowing.user, self.user)

    def test_create_borrowing_fails_when_no_books(self):
        """Test that borrowing fails when no books are available"""
        book = sample_book(inventory=0)
        payload = {
            "book": book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }

        with self.assertRaises(ValueError):
            res = self.client.post(BORROWING_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_borrowings_by_user(self):
        """Test filtering borrowings by user"""
        other_user = get_user_model().objects.create_user(
            "other@test.com", "password123"
        )
        book = sample_book()
        sample_borrowing(user=self.user, book=book)
        sample_borrowing(user=other_user, book=book)

        res = self.client.get(BORROWING_URL, {"user_id": self.user.id})

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_borrowings_by_is_active(self):
        """Test filtering borrowings by active status"""
        book = sample_book()
        active_borrowing = sample_borrowing(user=self.user, book=book)
        returned_borrowing = sample_borrowing(
            user=self.user,
            book=book,
            actual_return_date=date.today() - timedelta(days=1),
        )

        res = self.client.get(BORROWING_URL, {"is_active": "true"})

        serializer = BorrowingSerializer(active_borrowing)
        self.assertIn(serializer.data, res.data)

        serializer = BorrowingSerializer(returned_borrowing)
        self.assertNotIn(serializer.data, res.data)

    def test_retrieve_borrowing_detail(self):
        """Test retrieving a borrowing's detail"""
        book = sample_book()
        borrowing = sample_borrowing(user=self.user, book=book)

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingSerializer(borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_return_borrowing(self):
        """Test returning a borrowed book"""
        book = sample_book()
        borrowing = sample_borrowing(user=self.user, book=book)
        url = return_url(borrowing.id)
        payload = {"actual_return_date": date.today()}

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        borrowing.refresh_from_db()
        self.assertEqual(borrowing.actual_return_date, date.today())
        self.assertEqual(book.inventory, 10)


class AdminBorrowingApiTests(TestCase):
    """Test the borrowings API (admin user)"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            "admin@test.com", "adminpass", is_staff=True
        )
        self.client.force_authenticate(self.admin_user)

    def test_list_all_borrowings(self):
        """Test listing all borrowings"""
        book = sample_book()
        user = get_user_model().objects.create_user(
            "other@test.com", "password123"
        )
        sample_borrowing(user=user, book=book)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
