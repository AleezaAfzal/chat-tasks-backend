import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from openai import OpenAI
from database_helpers import connect, insert, entry_exists

load_dotenv()
oai_key = os.getenv('OPENAI_API_KEY')
front_url = os.getenv('FRONTEND_URL')
gpt_model = os.getenv('GPT_VERSION')
token_limit = int(os.getenv('GPT_TOKEN_LIMIT'))
prolific_code = os.getenv('PROLIFIC_CODE')
prolific_url = os.getenv('PROLIFIC_URL')

app = Flask(__name__)

gpt_client = OpenAI(api_key = oai_key)

CORS(app, origins = [front_url])

@app.route('/chat', methods = ['POST'])
def send_message():
    try:
        req = request.get_json()
        messages = req['messages']

        completion = gpt_client.chat.completions.create(
            model = str(gpt_model),
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
            max_tokens = token_limit
        )

        full_res = completion.model_dump()

        return {'response': full_res}, 200
    except Exception as e:
        return {'error': str(e)}, 500
    
@app.route('/save', methods = ['POST'])
def save_data():
    try:
        req = request.get_json()
        newDataRecord = {
            '_id': req['participantId'],
            'messages': req['messages'],
            'tasks': req['tasks'],
            'condition': req['condition']
        }

        db = connect()
        collection = db['data']
        
        insertSuccess = insert(newDataRecord, collection)
        if insertSuccess == True:
            return {'message': 'OK', 'prolificCode': prolific_code, 'prolificUrl': prolific_url}, 201

        return {'message': 'Record already exists'}, 304
    except Exception as e:
        return {'error': str(e)}, 500
    
@app.route('/check_participation', methods = ['POST'])
def check_participation():
    try:
        req = request.get_json()
        db = connect()
        collection = db['data']

        pid_exists = entry_exists(str(req['id']), collection)
        if pid_exists == True:
            return {'participated': True}, 302

        return {'participated': False}, 204
    except Exception as e:
        return {'error': str(e)}, 500