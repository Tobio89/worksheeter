import setENV

import os
import click

from flask_migrate import Migrate
from app import create_app, db
from app.models import Worksheets


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict() # Add DB models here.

# @app.cli.command()
# @click.argument()

# The DB init / create_all stuff needs to be run first.