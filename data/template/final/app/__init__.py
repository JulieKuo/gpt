"""Initialize Flask app."""
from flask import Flask

"""Construct core Flask application with embedded Dash app."""
server = Flask(__name__, static_url_path='', static_folder='../frontend/build')
