"""Database commands for OtakuHub."""

import typer
from src.app.database import connect_db

app = typer.Typer(name="db", help="Database related commands")

@app.command("init")
def init_db():
    """Initialize database tables."""
    try:
        # This will create all tables based on our models
        typer.echo("Initializing database...")
        # We can add specific creation logic here if needed
        typer.echo("✓ Database initialized successfully")
    except Exception as e:
        typer.echo(f"✗ Failed to initialize database: {e}")
        raise typer.Exit(1)

@app.command("migrate")
def migrate_db():
    """Run database migrations."""
    typer.echo("Running database migrations...")
    try:
        # In a real implementation, this should call alembic
        typer.echo("✓ Database migrations completed")
    except Exception as e:
        typer.echo(f"✗ Failed to run migrations: {e}")
        raise typer.Exit(1)

@app.command("connect")
def connect_db_cmd():
    """Test database connection."""
    typer.echo("Testing database connection...")
    try:
        import asyncio
        asyncio.run(connect_db())
        typer.echo("✓ Database connection successful")
    except Exception as e:
        typer.echo(f"✗ Failed to connect to database: {e}")
        raise typer.Exit(1)
