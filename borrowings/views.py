from datetime import date

import logging

from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    ReturnBookSerializer,
)

from django_q.tasks import async_task

logger = logging.getLogger(__name__)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return {
            "list": BorrowingListSerializer,
            "retrieve": BorrowingDetailSerializer,
        }.get(self.action, BorrowingSerializer)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if not user.is_staff:
            queryset = queryset.filter(user=user)
        elif user_id:
            queryset = queryset.filter(user_id=user_id)

        if is_active:
            queryset = queryset.filter(
                actual_return_date__isnull=(is_active.lower() == "true")
            )

        return queryset

    @extend_schema(
        summary="Return a borrowed book",
        description=(
            "Marks a book as returned for the specified borrowing record. "
            "If the book is already returned, a 400 Bad Request response is returned. "
            "If successful, a notification is scheduled about the return."
        ),
        responses={
            200: ReturnBookSerializer,
            400: OpenApiResponse(description="This book has already been returned."),
        },
    )
    @action(detail=True, methods=["put"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"detail": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReturnBookSerializer(
            borrowing, data={"actual_return_date": date.today()}, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            self._schedule_notification("notify_book_returned_task", borrowing.id)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        self._schedule_notification("notify_new_borrowing_task", borrowing.id)

    def _schedule_notification(self, task_name, borrowing_id):
        try:
            async_task(f"borrowings.tasks.{task_name}", borrowing_id)
            logger.info(f"Notification scheduled for borrowing ID: {borrowing_id}")
        except Exception as e:
            logger.error(
                f"Failed to schedule notification for borrowing ID {borrowing_id}: {e}"
            )
