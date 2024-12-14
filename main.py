from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from dotenv import load_dotenv
import typing_extensions as typing
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

class Roadmap(typing.TypedDict):
    format : str
    task : str
    phase : int

class Module(typing.TypedDict):
    header : str
    module_inside_info : str
    module : int

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
    return "Welcome to my AI-World"

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
                    {"role": "user",
                    "parts": [
                        {
                            "text": f"Resolve the user query related to this task: {task}"
                            +"(Provide output in simple format like without using bold letters or any such things and give only output and where we have to change line add a HTML line changing tag their only)."
                            }
                        ]
                    }
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
        
        generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
        "response_schema" : list[Roadmap]
        }
        
        model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        )

        try:
            chat_session = model.start_chat(
            history=[
                {
                    "role": "user",  # Adjust to "system" or "user" based on your need
                    "parts": [
                        {"text": '''Prepare a roadmap for the provided task on the daily, hourly, weekly or , monthly basis as per need by a task to complete it for basics to deep. 
                        its a strict order that roadmap is only in hourly, daily, weekly or monthly format as per needed by task and the task we have to accomplish in it.
                        
                        in json format you have to arrange things as per given:

                        format : in which basis you set the timetable like weekly , hourly , daily or monthly basis.
                        phase : day , week , hour or month number.
                        task : the task you have to fulfill.

                        Note : Provide output in only one format i.e. if output is in daily format it only be in daily format.
                        '''
                            }
                        ]
                    }
                ]
            )
            response = chat_session.send_message(task)
            response = json.loads(response.text)
            res = ""
            for o in response:
                res = res + f'{o['format']} : {o['phase']}'+' <br> '+ o['task']+' <br> <br> '

            return jsonify({"format" : response[0]["format"] , 
                "roadmap" : res})
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
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
            "response_schema" : list[Module]
        }
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
        )

        try :
            chat_session = model.start_chat(
                history = [{
                    "role" : "user" ,
                    "parts" : [{
                        "text" : '''Divide my task into modules from a very basic level to advance in such a way that user have no idea about it 
                        so provide a detail regards every module also and make it easier for user .

                        In json format you have to arrange things as like,

                        header : the header which consists of the above part of starting a module.
                        module : contains the module number.
                        module_inside_info : contains everything inside a single module in detail as user have null knowledge regards the task.
                        '''
                    }]
                }]
            )
            response = chat_session.send_message(task)

            json_output = json.loads(response.text)
            response = json_output
            
            res = ""
            for o in response:
                res = res + f'{o['header']}' + ' <br> '+ f'Module : {o['module']}'+' <br> '+ o['module_inside_info'] + '<br> <br> '

            return jsonify({"module" : res})
        except Exception as e:
            return jsonify({"error" : str(e)}) , 500

if __name__ == "__main__":
    app.run(debug=True)