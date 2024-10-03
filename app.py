from datetime import timedelta

from decouple import config
from flask import Flask, jsonify, session
from flask_session import Session

from openai import OpenAI

from instruction import instructions

from helpers import functions, available_functions

import json

openAI_key = config('OPENAI_KEY')

client = OpenAI(api_key=openAI_key)

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/chat')
def chat():
    # user_message = request.json.get('message')
    user_message = "need a 1111 product details"
    # user_message = "Sale 10 quantity of 1111 product by cash"
    # user_message = "delete 1111 product"
    # user_message = None

    if not user_message:
        return jsonify({'message': 'No message provided'}), 400

    # Initialize or fetch conversation history for the session
    if 'messages' not in session:
        session['messages'] = [{
            "role": "system",
            "content": instructions
        }]

    # Add the user's message to the conversation
    session['messages'].append({"role": "user", "content": user_message})

    # Call the OpenAI API with current conversation
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=session['messages'],
        functions=functions,
        function_call="auto"
    )

    response_message = response.choices[0].message
    response_content = response.choices[0].message.content

    # store chatbot response message to session message tread
    session['messages'].append(response_message)

    try:
        function_name = response.choices[0].message.function_call.name
        function_args = json.loads(response.choices[0].message.function_call.arguments)
    except:
        function_name = None
        function_args = {}

        # Handle function call if necessary
    if function_name and function_args is not {}:
        function_message = available_functions[function_name](**function_args)

        # store function response message to session message tread
        session['messages'].append(
            {
                "role": "function",
                "name": function_name,
                "content": function_message
            }
        )

        # Call the OpenAI API with current conversation
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=session['messages'],
        )

        response_message = response.choices[0].message
        response_content = response.choices[0].message.content
        session['messages'].append(response_message)

    # Return the chatbot response
    return jsonify(
        {"message": response_content}
    ), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
