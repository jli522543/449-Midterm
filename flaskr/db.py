import click
import pymongo
from flask import current_app, g

def get_db():
    if 'db' not in g:
        CONNECTION_STRING = ""
        client = pymongo.MongoClient(CONNECTION_STRING) 
        db = client.get_database('449')
        g.db = db
    return g.db


# def close_db(e=None):
#     db = g.pop('db', None)

#     if db is not None:
#         db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    # app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)