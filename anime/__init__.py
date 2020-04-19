import flask


app = flask.Flask(__name__)  # pylint: disable=invalid-name


import anime.views  # noqa: E402  pylint: disable=wrong-import-position
import anime.model # noqa: E402  pylint: disable=wrong-import-position

