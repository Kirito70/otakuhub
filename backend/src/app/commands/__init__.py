"""Command interface for OtakuHub backend."""

from typer import Typer
from . import db
from . import celery
from . import seed

# Create main CLI app
app = Typer(
    name="otakuhub",
    help="OtakuHub backend CLI commands",
    no_args_is_help=True,
)

# Include sub-commands
app.add_typer(db.app, name="db", help="Database related commands")
app.add_typer(celery.app, name="celery", help="Celery worker/task commands")
app.add_typer(seed.app, name="seed", help="Data seed commands")
