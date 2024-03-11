import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from openai import OpenAI

load_dotenv()
oai_key = os.getenv('OPENAI_API_KEY')
front_url = os.getenv('FRONTEND_URL')

app = Flask(__name__)

gpt_client = OpenAI(api_key = oai_key)

CORS(app, origins = [front_url])

@app.route('/chat', methods = ['POST'])
def send_message():
    try:
        req = request.get_json()
        messages = req['messages']

        completion = gpt_client.chat.completions.create(
            model = 'gpt-4-vision-preview',
            messages = [
                {
                    'role': str(m['role']),
                    'content': [
                        { 'type': 'text', 'text': str(m['content']) },
                        { 'type': 'image_url', 'image_url': { 'url': str(m['image']), 'detail': 'low' }}
                    ]
                } 
                if 'image' in m.keys() else 
                {
                    'role': str(m['role']),
                    'content': str(m['content'])
                } 
                for m in messages
            ],
            max_tokens = 125
        )

        reply = str(completion.choices[0].message.content)

        return {'response': reply}, 200
    except Exception as e:
        print(e)
        return {'error': e}, 500