from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

@app.route("/" , methods = ["GET"])
def home():
    return

@app.route("/recommend", methods=["GET" , "POST"])
def recommend():
    if request.method == "GET":
        return "Use POST with task and query in the body"
    elif request.method == "POST":
        data = request.json
        task = data.get("task")
        query = data.get("query")

        if not task or not query:
            return jsonify({"error": "Task and query are required"}), 400

        try:
            chat_session = model.start_chat(
                history=[
                    {"role": "user", "parts": [{"text": f"Resolve the user query related to this task: {task}"}]}
                ]
            )
            response = chat_session.send_message(query)
            return jsonify({"recommendation": response.text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
@app.route("/recommendpriority" , methods= ["GET" , "POST"])
def recommendpriority():
    if request.method == "GET":
        return "Use POST with task"
    elif request.method == "POST":
        data = request.json
        task = data.get("task")

        if not task:
            return jsonify({"error" : "Task is required"}) , 400
        
        try:
            chat_session = model.start_chat(
                history = [
                    {
                        "role": "user", 
                        "parts": [
                            {"text": "Just give me the priority of the task I am giving to you in high, medium, or low; otherwise, respond 'not a task' in one word (any other word is restricted)."}
                        ]
                    }
                ]
            )
            response = chat_session.send_message(task)
            return jsonify({"priority" : response.text})
        except Exception as e:
            return jsonify({"error" : str(e)}) , 500

@app.route("/recommendroadmap" , methods= ["GET" , "POST"])
def recommendroadmap():
    if request.method == "GET":
        return "Use POST with task"
    elif request.method == "POST":
        data = request.json
        task = data.get("task")

        if not task:
            return jsonify({"error" : "Task is required"}) , 400
        
        try:
            chat_session = model.start_chat(
                history = [
                    {
                        "role": "user",  
                        "parts": [
                            {"text":"Prepare a roadmap for the provided task on the daily basis and hourly to achieve as must fast as a human can."}
                        ]
                    }
                ]
            )
            response = chat_session.send_message(task)
            return jsonify({"roadmap" : response.text})
        except Exception as e:
            return jsonify({"error" : str(e)}) , 500
        
@app.route("/recommendmodule" , methods= ["GET" , "POST"])
def recommendmodule():
    if request.method == "GET" :
        return "Use POST with task"
    elif request.method == "POST":
        data = request.json
        task = data.get("task")

        if not task:
            return jsonify({"error" : "Task is required"}) , 400
        
        try :
            chat_session = model.start_chat(
                history = [{
                    "role" : "user" ,
                    "parts" : [{
                        "text" : "Divide my task into modules in a very basic level in such a way that user have no idea about it so provide a detail regards every module also."
                    }]
                }]
            )
            response = chat_session.send_message(task)
            return jsonify({"module" : response.text})
        except Exception as e:
            return jsonify({"error" : str(e)}) , 500

if __name__ == "__main__":
    app.run(debug=True)