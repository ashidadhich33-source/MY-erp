"""
Command Line Interface for database operations.

Usage:
    python -m app.utils.cli init-db          # Initialize database with tables
    python -m app.utils.cli seed-data       # Populate database with sample data
    python -m app.utils.cli reset-db         # Reset database (drop all tables and recreate)
"""

import sys
import click
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command

from ..core.database import engine, Base
from .seed_data import run_seed


@click.group()
def cli():
    """Database management commands."""
    pass


@cli.command()
def init_db():
    """Initialize database with all tables."""
    click.echo("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    click.echo("✅ Database tables created successfully!")


@cli.command()
def seed_data():
    """Populate database with sample data."""
    from ..core.database import SessionLocal

    click.echo("Seeding database with sample data...")
    db = SessionLocal()
    try:
        run_seed(db)
        click.echo("✅ Database seeded successfully!")
    except Exception as e:
        click.echo(f"❌ Error seeding database: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


@cli.command()
def reset_db():
    """Reset database (drop all tables and recreate)."""
    click.echo("⚠️  This will delete all data! Are you sure?")
    if not click.confirm("Do you want to continue?"):
        click.echo("Operation cancelled.")
        return

    click.echo("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    click.echo("Recreating all tables...")
    Base.metadata.create_all(bind=engine)

    click.echo("✅ Database reset successfully!")


@cli.command()
def create_migration():
    """Create a new Alembic migration."""
    from app.core.database import Base

    # Import all models to ensure they are registered
    from app.models import *

    click.echo("Creating new migration...")
    alembic_cfg = Config("alembic.ini")

    try:
        command.revision(alembic_cfg, message="Auto-generated migration", autogenerate=True)
        click.echo("✅ Migration created successfully!")
    except Exception as e:
        click.echo(f"❌ Error creating migration: {e}", err=True)
        sys.exit(1)


@cli.command()
def upgrade_db():
    """Upgrade database to latest migration."""
    click.echo("Upgrading database...")
    alembic_cfg = Config("alembic.ini")

    try:
        command.upgrade(alembic_cfg, "head")
        click.echo("✅ Database upgraded successfully!")
    except Exception as e:
        click.echo(f"❌ Error upgrading database: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()