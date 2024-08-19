from django.db import models


class Book(models.Model):
    COVER_CHOICES = [
        ('HARD', 'Hardcover'),
        ('SOFT', 'Softcover'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def borrow(self):
        if self.inventory > 0:
            self.inventory -= 1
            self.save()
        else:
            raise ValueError(
                "There are no copies of this book available"
            )

    def return_book(self):
        self.inventory += 1
        self.save()

    def __str__(self):
        return self.title
