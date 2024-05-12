import os

from flask import Flask
from . import db
from . import auth
from . import home

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'CSUFTitans1957'
    
    app.register_blueprint(auth.bp)
    db.init_app(app)


    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    return app