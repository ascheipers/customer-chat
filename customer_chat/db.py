import sqlite3
import uuid
from datetime import datetime

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('create-agent')
@click.argument('email')
@click.argument('password')
@click.argument('display_name')
def create_agent_command(email, password, display_name):
    db = get_db()
    db.execute(
        "INSERT INTO agent (id, email, display_name, password_hash) VALUES (?, ?, ?, ?)",
        (str(uuid.uuid4()), email, display_name, generate_password_hash(password))
    )
    db.commit()


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_agent_command)
