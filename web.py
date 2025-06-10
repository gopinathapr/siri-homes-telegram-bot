from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# This code is a simple Flask web application that serves an index page and handles form submissions.


if __name__ == '__main__':
    app.run(debug=True, port=8080)
