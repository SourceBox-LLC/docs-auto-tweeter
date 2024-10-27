import logging
from flask import Flask, render_template, request, Response
from agent import Agent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route("/")
def index():
    logging.info("Rendering index page")
    return render_template("index.html")

@app.route('/agent', methods=['POST', 'GET'])
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

if __name__ == "__main__":
    logging.info("Starting Flask app")
    app.run(debug=True)
