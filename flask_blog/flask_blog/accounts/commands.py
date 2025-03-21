import click
from flask.cli import with_appcontext
from flask_blog.container import container
import os
from datetime import datetime, timezone

from flask_blog.extensions import db

@click.command('create-superuser')
@click.option('--email', default=None, help='Superuser email')
@click.option('--password', default=None, help='Superuser password')
@with_appcontext
def create_superuser(email, password):
    """Creates a superuser account."""
    user_service = container.user_service

    email = email or os.environ.get('ADMIN_EMAIL', 'admin@blog.com')
    password = password or os.environ.get('ADMIN_PASSWORD', 'admin')
    
    existing_user = user_service.get_user_by_email(email)

    if existing_user:
        click.echo(f"Superuser with email {email} already exists.")
        return
    
    try:
        user_service.create_user(email, password, "Admin", True, True, datetime.now(timezone.utc))

        click.echo(f"Superuser {email} created successfully!")

    except Exception as e:
        db.session.rollback()
        click.echo(f"Error creating superuser: {str(e)}")
        raise e

# Register this command with your Flask app
def register_commands(app):
    app.cli.add_command(create_superuser)