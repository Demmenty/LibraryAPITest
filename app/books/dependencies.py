import re

from fastapi import HTTPException, Path, status


def validate_isbn_10(
    isbn: str = Path(..., title="ISBN", description="ISBN-10 number")
) -> str:
    """
    Validate the ISBN-10 number.

    Args:
        isbn (str): ISBN-10 number.

    Raises:
        HTTPException 422: If the ISBN-10 number is not valid.

    Returns:
        str: The validated ISBN-10 number.
    """

    is_valid = re.match(r"^\d{10}$", isbn.strip())
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ISBN must be a 10-digit number",
        )

    return isbn
