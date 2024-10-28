import logging
from flask import Flask, render_template, request, Response, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from agent import Agent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tweets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Define a Tweet model
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create the database tables
with app.app_context():
    db.create_all()

def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    wrap.__name__ = f.__name__
    return wrap

@app.route("/")
@login_required
def index():
    logging.info("Rendering index page")
    return render_template("index.html")

@app.route('/agent', methods=['POST', 'GET'])
@login_required
def agent():
    if request.method == 'POST':
        data = request.form['prompt']
        app.config['PROMPT'] = data  # Store the prompt in the app config
        return '', 204  # Return no content for POST

    if request.method == 'GET':
        prompt = app.config.get('PROMPT', '')
        return Response(stream_agent_response(prompt), mimetype='text/event-stream')

def stream_agent_response(prompt):
    for chunk in Agent(prompt):
        logging.info(f"Streaming chunk: {chunk}")
        yield f"data: {chunk}\n\n"

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == '42069':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid password", 401
    return render_template('login.html')

if __name__ == "__main__":
    logging.info("Starting Flask app")
    app.run(debug=True)
