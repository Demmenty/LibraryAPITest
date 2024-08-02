import click
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.auth.routers import router as auth_routers
from app.books.models import Base  # -> migrations/env.py
from app.books.routers import router as books_routers
from app.commands import createadmin
from app.config import app_configs, settings
from app.users.routers import router as users_routers


app = FastAPI(**app_configs)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    """Check if the server is up and running"""

    return {"status": "ok"}


@click.group()
def cli():
    pass


cli.add_command(createadmin)


app.include_router(auth_routers, prefix="/auth", tags=["Authentication"])
app.include_router(users_routers, prefix="/users", tags=["User Management"])
app.include_router(books_routers, prefix="/books", tags=["Book Management"])


if __name__ == "__main__":
    import uvicorn

    cli()
    uvicorn.run(app)
