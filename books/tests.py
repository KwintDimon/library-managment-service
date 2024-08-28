from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from books.serializers import BookSerializer

BOOK_URL = reverse("books:book-list-create")


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


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_books(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOK_URL)

        books = Book.objects.order_by("id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 15,
            "daily_fee": 2.00,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_create_book_forbidden_for_non_admin(self):
        self.user.is_staff = False
        self.user.save()

        payload = {
            "title": "Forbidden Book",
            "author": "Forbidden Author",
            "cover": "HARD",
            "inventory": 20,
            "daily_fee": 3.00,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
