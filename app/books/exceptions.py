from app.exceptions import BadRequest, NotFound


class ErrorCode:
    BOOK_NOT_FOUND = "Book(s) not found."
    CATEGORY_NOT_FOUND = "Category(s) not found."
    SEARCH_QUERY_EMPTY = "Search query cannot be empty."
    ISBN_NOT_VALID ="ISBN must be a 10-digit number"


class BookNotFound(NotFound):
    DETAIL = ErrorCode.BOOK_NOT_FOUND


class CategoryNotFound(NotFound):
    DETAIL = ErrorCode.CATEGORY_NOT_FOUND


class SearchQueryEmpty(BadRequest):
    DETAIL = ErrorCode.SEARCH_QUERY_EMPTY


class NotValidISBN(BadRequest):
    DETAIL = ErrorCode.ISBN_NOT_VALID
