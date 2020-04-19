'''anime app main view file'''

import flask
import anime

@anime.app.route('/')
def index():
    return "hello world!"