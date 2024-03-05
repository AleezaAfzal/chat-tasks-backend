import os
from dotenv import load_dotenv
from flask import Flask, request
#from flask_cors import CORS
from openai import OpenAI

load_dotenv()
oai_key = os.getenv('OPENAI_API_KEY')
front_url = os.getenv('FRONTEND_URL')

app = Flask(__name__)

gpt_client = OpenAI(api_key = oai_key)

#CORS (app, origins = [front_url])

@app.route('/chat', methods = ['POST'])
def send_message():
    try:
        req = request.get_json()
        body = req['data']
        message = str(body['message'])
        print(message)

        completion = gpt_client.chat.completions.create(
            model = 'gpt-3.5-turbo',
            messages = [
                { "role" : "user", "content": message }
            ],
            max_tokens = 4
        )

        reply = str(completion.choices[0].message.content)

        print(reply)

        return {'response': reply}, 200
    except Exception as e:
        print(e)
        return {'error': e}, 500