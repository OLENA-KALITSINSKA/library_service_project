from django_q.tasks import async_task
from borrowings.notifications import (
    notify_new_borrowing,
    notify_book_returned,
)
from borrowings.models import Borrowing


def notify_new_borrowing_task(borrowing_id: int) -> None:
    borrowing = Borrowing.objects.get(id=borrowing_id)
    notify_new_borrowing(borrowing)


def notify_book_returned_task(borrowing_id: int) -> None:
    borrowing = Borrowing.objects.get(id=borrowing_id)
    notify_book_returned(borrowing)


def schedule_notification_task(task_name: str, borrowing_id: int) -> None:
    async_task(task_name, borrowing_id)
