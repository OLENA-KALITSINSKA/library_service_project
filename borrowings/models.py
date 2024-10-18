from django.db import models
from django.conf import settings
from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.book.inventory <= 0:
                raise ValueError("No more copies of the book " "available to borrow.")
            self.book.inventory -= 1
            self.book.save()

        super().save(*args, **kwargs)

    def return_book(self):
        if self.actual_return_date:
            self.book.inventory += 1
            self.book.save()

    def __str__(self):
        return (
            f"{self.book.title} borrowed by " f"{self.user.email} on {self.borrow_date}"
        )
