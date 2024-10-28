import logging
import json
from flask import Flask, render_template, request, Response, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from agent import Agent
from langchain_core.messages import AIMessage

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.debug(f"Received POST data: {data}")
        app.config['PROMPT'] = data  # Store the prompt in the app config
        return '', 204  # Return no content for POST

    if request.method == 'GET':
        prompt = app.config.get('PROMPT', '')
        logging.debug(f"Using prompt for GET: {prompt}")
        return Response(stream_agent_response(prompt), mimetype='text/event-stream')

def stream_agent_response(prompt):
    for chunk in Agent(prompt):
        logging.debug(f"Streaming chunk: {chunk}")
        
        # Convert the AIMessage object to a dictionary or JSON-serializable format
        if isinstance(chunk, dict):
            # Assuming the AIMessage is within a dictionary structure
            messages = chunk.get('agent', {}).get('messages', [])
            for message in messages:
                if isinstance(message, AIMessage):
                    # Convert AIMessage to a dictionary
                    message_dict = {
                        'content': message.content,
                        'additional_kwargs': message.additional_kwargs,
                        'response_metadata': message.response_metadata,
                        'id': message.id,
                        'usage_metadata': message.usage_metadata
                    }
                    logging.debug(f"Serialized message: {message_dict}")
                    yield f"data: {json.dumps(message_dict)}\n\n"
                else:
                    logging.debug(f"Serialized message: {message}")
                    yield f"data: {json.dumps(message)}\n\n"
        else:
            logging.error("Chunk is not a dictionary and cannot be serialized to JSON.")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        logging.debug(f"Login attempt with password: {password}")
        if password == '42069':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid password", 401
    return render_template('login.html')

if __name__ == "__main__":
    logging.info("Starting Flask app")
    app.run(debug=True)
