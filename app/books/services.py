from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.books.models import AuthorModel, BookModel, CategoryModel
from app.books.schemas import Author, Book, BookSearchRequest, Category


class BookService:

    async def create_book(self, db: AsyncSession, book: Book) -> BookModel:
        """
        Creates a book in the database.

        Args:
            db (AsyncSession): The async session to interact with the database.
            book (Book): The book object containing the book details.

        Returns:
            BookModel: The newly created book model.
        """

        new_book = BookModel(
            isbn=book.isbn,
            title=book.title,
            language=book.language,
            publication_date=book.publication_date,
        )

        for author in book.authors:
            db_author = AuthorModel(name=author.name)
            new_book.authors.append(db_author)

        for category in book.categories:
            db_category = CategoryModel(name=category.name)
            new_book.categories.append(db_category)

        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)

        return new_book

    async def create_author(self, db: AsyncSession, author: Author) -> AuthorModel:
        """
        Create an author in the database.

        Args:
            db (AsyncSession): The database session.
            author (Author): The author data to be created.

        Returns:
            AuthorModel: The newly created author.
        """

        new_author = AuthorModel(name=author.name)
        db.add(new_author)
        await db.commit()
        await db.refresh(new_author)

        return new_author

    async def create_category(
        self, db: AsyncSession, category: Category
    ) -> CategoryModel:
        """
        Creates a new book category in the database.

        Args:
            db (AsyncSession): The async database session.
            category (Category): The category data to be created.

        Returns:
            CategoryModel: The newly created category model.
        """

        new_category = CategoryModel(name=category.name)
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)

        return new_category

    async def get_book_by_isbn(self, db: AsyncSession, isbn: int) -> BookModel | None:
        """
        Gets a book by its ISBN from the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            isbn (int): The ISBN of the book to retrieve.

        Returns:
            BookModel | None: The book with the specified ISBN, or None if not found.
        """

        result = await db.execute(select(BookModel).filter(BookModel.isbn == isbn))
        book = result.scalars().first()

        return book

    async def get_books_by_category(
        self, db: AsyncSession, category: str
    ) -> list[BookModel]:
        """
        Retrieves a list of books by category from the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            category (str): The category of the books to retrieve.

        Returns:
            list[BookModel]: A list of BookModel objects corresponding to the given category.
        """

        result = await db.execute(
            select(BookModel).filter(BookModel.categories.any(name=category.lower()))
        )
        books = result.scalars().all()

        return books

    async def search_books(
        self,
        db: AsyncSession,
        search: BookSearchRequest,
    ) -> list[BookModel]:

        query = select(BookModel)
        if search.title:
            query = query.filter(BookModel.title == search.title)
        if search.author:
            query = query.filter(
                BookModel.authors.any(AuthorModel.name == search.author)
            )
        if search.publication_date:
            query = query.filter(BookModel.publication_date == search.publication_date)
        if search.isbn:
            query = query.filter(BookModel.isbn == search.isbn)

        result = await db.execute(query)
        books = result.scalars().all()

        return books

    async def get_author_by_name(
        self, db: AsyncSession, name: str
    ) -> AuthorModel | None:
        """
        Retrieves an author by name from the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            name (str): The name of the author to retrieve.

        Returns:
            AuthorModel | None: The retrieved author, or None if not found.
        """

        result = await db.execute(select(AuthorModel).filter_by(name=name))
        author = result.scalars().first()

        return author

    async def get_category_by_id(
        self, db: AsyncSession, id: int
    ) -> CategoryModel | None:
        """
        Retrieves a category by ID from the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            id (int): The ID of the category to retrieve.

        Returns:
            CategoryModel | None: The retrieved category, or None if not found.
        """

        result = await db.execute(select(CategoryModel).filter_by(id=id))
        category = result.scalars().first()

        return category

    async def get_all_categories(self, db: AsyncSession) -> list[CategoryModel]:
        """
        Retrieves all book categories from the database.

        Args:
            db (AsyncSession): The asynchronous database session.

        Returns:
            list[CategoryModel]: A list of CategoryModel objects.
        """

        result = await db.execute(select(CategoryModel))
        categories = result.scalars().all()

        return categories
