import json

from fastapi import APIRouter, BackgroundTasks, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_admin_from_refresh_token,
    get_user_from_access_token,
)
from app.books.dependencies import validate_isbn_10
from app.books.exceptions import BookNotFound, CategoryNotFound
from app.books.schemas import (
    Book,
    Books,
    BookSearchRequest,
    CategoriesResponse,
    CategoryResponse,
    UserUnavailableCategoriesChangeRequest,
    UserUnavailableCategoriesResponse,
)
from app.books.services import BookService
from app.database import get_db
from app.external.google_books_api.services import GoogleBooksService
from app.external.redis_db.schemas import RedisData
from app.external.redis_db.services import RedisService
from app.users.exceptions import UserNotFound
from app.users.models import UserModel
from app.users.services import UserService

router = APIRouter()


@router.get("/by-isbn/{isbn}", response_model=Book)
async def get_book_by_isbn(
    worker: BackgroundTasks,
    isbn: str = Depends(validate_isbn_10),
    db: AsyncSession = Depends(get_db),
    book_service: BookService = Depends(BookService),
    google_books_api: GoogleBooksService = Depends(GoogleBooksService),
    cache: RedisService = Depends(RedisService),
    user: UserModel = Depends(get_user_from_access_token),
) -> dict:
    """Retrieves a book details by ISBN"""

    cached_book = await cache.get_by_key(f"book:{isbn}")
    if cached_book:
        book = Book(**json.loads(cached_book))
        return book

    book_db = await book_service.get_book_by_isbn(db, isbn)
    if book_db:
        book = Book.model_validate(book_db)
    else:
        book = await google_books_api.get_book_by_isbn(isbn)
        if not book:
            raise BookNotFound()

        worker.add_task(book_service.create_book, db, book)

    cache_data = RedisData(key=f"book:{isbn}", value=book.model_dump_json(), ttl=3600)
    worker.add_task(cache.set_key, cache_data)

    return book


@router.get("/by-category/{category_name}", response_model=Books)
async def get_books_by_category(
    category_name: str,
    worker: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    book_service: BookService = Depends(BookService),
    cache: RedisService = Depends(RedisService),
    user: UserModel = Depends(get_user_from_access_token),
) -> dict:
    """Retrieves books details by category name"""

    cached_books = await cache.get_by_key(f"book:{category_name}")
    if cached_books:
        books = Books(
            books=[Book(**json.loads(book)) for book in json.loads(cached_books)]
        )
        return books

    books_db = await book_service.get_books_by_category(db, category_name)
    if not books_db:
        raise BookNotFound()

    books = Books(books=[Book.model_validate(book) for book in books_db])

    cache_data = RedisData(
        key=f"book:{category_name}",
        value=json.dumps([book.model_dump_json() for book in books.books]),
        ttl=600,
    )
    worker.add_task(cache.set_key, cache_data)

    return books


@router.get("/category/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    worker: BackgroundTasks,
    category_id: int = Path(..., title="Category ID in URL"),
    db: AsyncSession = Depends(get_db),
    book_service: BookService = Depends(BookService),
    cache: RedisService = Depends(RedisService),
    user: UserModel = Depends(get_user_from_access_token),
) -> dict:
    """Retrieves category details by ID"""

    cached_category = await cache.get_by_key(f"category:{category_id}")
    if cached_category:
        category = CategoryResponse(**json.loads(cached_category))
        return category

    category_db = await book_service.get_category_by_id(db, category_id)
    if not category_db:
        raise CategoryNotFound()

    category = CategoryResponse.model_validate(category_db)

    cache_data = RedisData(
        key=f"category:{category_id}",
        value=category.model_dump_json(),
        ttl=3600,
    )
    worker.add_task(cache.set_key, cache_data)

    return category


@router.get("/categories", response_model=CategoriesResponse)
async def get_all_categories(
    worker: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    book_service: BookService = Depends(BookService),
    cache: RedisService = Depends(RedisService),
    user: UserModel = Depends(get_user_from_access_token),
) -> dict:
    """Retrieves all categories"""

    cached_categories = await cache.get_by_key("categories")
    if cached_categories:
        categories = CategoriesResponse(
            categories=[
                CategoryResponse(**json.loads(category))
                for category in json.loads(cached_categories)
            ]
        )
        return categories

    categories_db = await book_service.get_all_categories(db)
    if not categories_db:
        raise CategoryNotFound()

    categories = CategoriesResponse(
        categories=[
            CategoryResponse.model_validate(category) for category in categories_db
        ]
    )

    cache_data = RedisData(
        key="categories",
        value=json.dumps(
            [category.model_dump_json() for category in categories.categories]
        ),
        ttl=600,
    )
    worker.add_task(cache.set_key, cache_data)

    return categories


@router.post("/search", response_model=Books)
async def search_books(
    worker: BackgroundTasks,
    search: BookSearchRequest,
    db: AsyncSession = Depends(get_db),
    book_service: BookService = Depends(BookService),
    cache: RedisService = Depends(RedisService),
    user: UserModel = Depends(get_user_from_access_token),
) -> dict:
    """Retrieves books details based on the search query"""

    cached_books = await cache.get_by_key(f"book:{search}")
    if cached_books:
        books = Books(
            books=[Book(**json.loads(book)) for book in json.loads(cached_books)]
        )
        return books

    books_db = await book_service.search_books(db, search)
    if not books_db:
        raise BookNotFound()

    books = Books(books=[Book.model_validate(book) for book in books_db])

    cache_data = RedisData(
        key=f"book:{search}",
        value=json.dumps([book.model_dump_json() for book in books.books]),
        ttl=1200,
    )
    worker.add_task(cache.set_key, cache_data)

    return books


@router.get(
    "/unavailable_categories/user/{user_id}",
    response_model=UserUnavailableCategoriesResponse,
)
async def get_user_unavailable_categories(
    user_id: int = Path(..., title="User ID in URL"),
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(UserService),
    admin: UserModel = Depends(get_admin_from_refresh_token),
) -> dict:
    """Only for admins. Retrieves user's unavailable categories"""

    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise UserNotFound()

    return UserUnavailableCategoriesResponse(
        user_id=user_id,
        unavailable_categories=user.unavailable_book_categories,
    )


@router.post(
    "/unavailable_categories/user/{user_id}/add",
    response_model=UserUnavailableCategoriesResponse,
)
async def add_user_unavailable_categories(
    data: UserUnavailableCategoriesChangeRequest,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(UserService),
    admin: UserModel = Depends(get_admin_from_refresh_token),
) -> dict:
    """Only for admins. Adds unavailable book categories to user"""

    user = await user_service.add_unavailable_categories(
        db, data.user_id, data.categories_id
    )

    return UserUnavailableCategoriesResponse(
        user_id=user.id,
        unavailable_categories=[
            CategoryResponse.model_validate(category)
            for category in user.unavailable_book_categories
        ],
    )


@router.post(
    "/unavailable_categories/user/{user_id}/remove",
    response_model=UserUnavailableCategoriesResponse,
)
async def remove_user_unavailable_categories(
    data: UserUnavailableCategoriesChangeRequest,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(UserService),
    admin: UserModel = Depends(get_admin_from_refresh_token),
) -> dict:
    """Only for admins. Removes unavailable book categories from user"""

    user = await user_service.remove_unavailable_categories(
        db, data.user_id, data.categories_id
    )

    return UserUnavailableCategoriesResponse(
        user_id=user.id,
        unavailable_categories=[
            CategoryResponse.model_validate(category)
            for category in user.unavailable_book_categories
        ],
    )
