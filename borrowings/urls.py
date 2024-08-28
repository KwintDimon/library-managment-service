from django.urls import path

from borrowings.views import (
    BorrowingListCreateView,
    BorrowingDetailView,
    BorrowingReturnView
)

app_name = "borrowing"

urlpatterns = [
    path("", BorrowingListCreateView.as_view(), name="borrowing-list-create"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowing-detail"),
    path("<int:pk>/return/", BorrowingReturnView.as_view(), name="borrowing-return"),
]
