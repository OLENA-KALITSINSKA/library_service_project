import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

logger = logging.getLogger(__name__)


def send_telegram_message(message):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        response = requests.post(url, data=payload)
        response_data = response.json()

        if response.status_code != 200 or not response_data.get("ok", False):
            logger.error(
                f"Error sending message: {response_data.get('description', 'Unknown error')}"
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")


def notify_new_borrowing(borrowing):
    formatted_borrow_date = borrowing.borrow_date.strftime("%d-%m-%Y")
    formatted_expected_return_date = borrowing.expected_return_date.strftime("%d-%m-%Y")

    message = (
        f"📚 New Borrowing:\n"
        f"ID: {borrowing.id}\n"
        f"Book: {borrowing.book.title}\n"
        f"Borrower: {borrowing.user.email}\n"
        f"Borrow Date: {formatted_borrow_date}\n"
        f"Expected Return Date: {formatted_expected_return_date}"
    )
    send_telegram_message(message)


def notify_book_returned(borrowing):
    message = (
        f"📖 Book Returned:\n"
        f"ID: {borrowing.id}\n"
        f"Book: {borrowing.book.title}\n"
        f"Borrower: {borrowing.user.email}\n"
        f"Borrow Date: {borrowing.borrow_date}\n"
        f"Expected Return Date: {borrowing.expected_return_date}\n"
        f"Actual Return Date: {borrowing.actual_return_date}"
    )
    send_telegram_message(message)
