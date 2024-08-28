from django.urls import path

from books.views import BookListCreateView, BookDetailView

app_name = "books"

urlpatterns = [
    path("", BookListCreateView.as_view(), name="book-list-create"),
    path("<int:pk>/", BookDetailView.as_view(), name="book-detail"),
]
