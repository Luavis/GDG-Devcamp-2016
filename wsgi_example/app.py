from server import start_server
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return "hi!"

if __name__ == '__main__':
    start_server(app)
