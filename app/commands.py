import click

from app.database import async_session
from app.users.exceptions import EmailTaken, UsernameTaken
from app.users.schemas import User, UserRole
from app.users.services import UserService


@click.command()
@click.option("--username", prompt="Enter username", help="Admin username")
@click.option("--email", prompt="Enter email", help="Admin email")
@click.option(
    "--password", prompt="Enter password", hide_input=True, help="Admin password"
)
def createadmin(username, email, password):
    """
    Create an admin user with the provided username, email, and password.

    Args:
        username (str): The username of the admin.
        email (str): The email of the admin.
        password (str): The password of the admin.
    """

    import asyncio

    click.echo("Creating admin...")

    async def create_admin():
        async with async_session() as db:
            user_service = UserService()

            try:
                if await user_service.get_by_email(db, email):
                    raise EmailTaken()

                if await user_service.get_by_username(db, username):
                    raise UsernameTaken()

                admin_data = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "role": UserRole.ADMIN,
                }
                admin_user = User(**admin_data)
                await user_service.create_user(db, admin_user)
                click.echo("Admin created successfully!")

            except Exception as e:
                click.echo(f"Error creating admin: {e}")

    asyncio.run(create_admin())
