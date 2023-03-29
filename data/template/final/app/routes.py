import platform
import threading

from flask import current_app as app
from flask import render_template
from flask import send_from_directory

from utils.util import getSysMacAddr

operate_system = platform.system()


# @app.route('/')
# def red():
#    return redirect('/apps/dashboard')


@app.route("/", defaults={'path': ''})
# @app.route('/<path:path>')
def serve(path):
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/test')
def home():
    """Landing page."""
    return render_template(
        'base.html'
    )


@app.route('/mac-addr')
def get_mac_addr():
    return getSysMacAddr()


@app.route('/thread')
def get_thread():
    res = {
        'len': len(threading.enumerate()),
        'str': str(threading.enumerate())
    }
    return res


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')
