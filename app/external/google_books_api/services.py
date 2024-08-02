import asyncio
import logging

import httpx

from app.books.schemas import Author, Book, Category
from app.config import settings


class GoogleBooksService:

    BASE_URL: str = settings.GOOGLE_BOOKS_API

    @property
    def session(self):
        return httpx.AsyncClient(base_url=self.BASE_URL, timeout=10.0)

    async def fetch_data(self, url: str) -> dict | None:
        """
        Fetches data from the given URL using an HTTP GET request.

        Args:
            url (str): The URL to fetch data from.

        Returns:
            dict | None: The JSON response from the URL, or None if an error occurs.
        """

        try:
            async with self.session as session:
                response = await session.get(url)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logging.error(f"Error fetching data from Google Books API: {e}")
            return None

    async def get_book_by_isbn(self, isbn: str) -> Book | None:
        """
        Retrieves a book by its ISBN.

        Args:
            isbn (str): The ISBN of the book to retrieve.

        Returns:
            Book | None: The retrieved book if found, otherwise None.
        """

        url = f"{self.BASE_URL}/volumes?q=isbn:{isbn}"

        response_json = await self.fetch_data(url)
        if not response_json or response_json["totalItems"] == 0:
            return None

        loop = asyncio.get_event_loop()
        book = await loop.run_in_executor(
            None, lambda: self._parse_book_from_response(isbn, response_json)
        )

        return book

    def _parse_book_from_response(self, isbn: str, response_json: dict) -> Book:
        """
        Parses book information from the response JSON and returns a Book object.

        Args:
            isbn (str): The ISBN of the book.
            response_json (dict): The JSON response containing book information.

        Returns:
            Book: A Book object with the parsed book information.
        """

        book_info = response_json["items"][0]["volumeInfo"]

        book = Book(
            isbn=isbn,
            title=book_info["title"],
            language=book_info["language"],
            publication_date=book_info["publishedDate"],
            authors=[Author(name=author) for author in book_info.get("authors", [])],
            categories=[
                Category(name=category) for category in book_info.get("categories", [])
            ],
        )

        return book
