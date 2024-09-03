from flask import Flask,g
import mysql.connector
import os
import base64

def get_database_connection():
    if 'mydb' not in g:
        g.mydb = mysql.connector.connect(host="localhost",
                                          user="root",
                                          password="",
                                          database="jawicr")
    return g.mydb

def close_database_connection(exception):
    mydb = g.pop('mydb', None)
    if mydb is not None:
        mydb.close()

 # Define the custom filter
def b64encode(data):
    return base64.b64encode(data).decode('utf-8')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'FYP'

    app.config['DEBUG'] = True

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # 16 MB

    # Register the filter with Jinja2 environment
    app.jinja_env.filters['b64encode'] = b64encode

    # Register teardown function for database connection
    app.teardown_appcontext(close_database_connection)

    # Initialize database connection before each request
    @app.before_request
    def before_request():
        g.mydb = get_database_connection()

    from .views import views
    from .auth import auth
    
    app.register_blueprint(views,url_prefix = '/')
    app.register_blueprint(auth,url_prefix = '/')

    return app