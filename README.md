# Chat Tasks (Proxy Server)

The backend for our online study application. Handles messaging with GPT-4 and saving responses to the database.

## Running Locally

### Setup

Clone or download this repository and navigate to its root folder.

**(Recommended)** Create a new conda environment with Python and activate it:

```bash
conda create -n chat-tasks python

...

conda activate chat-tasks
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` file:

```bash
touch .env
```

Add in the url of your frontend and your OpenAI API key:

```.env
OPENAI_API_KEY=api_key_here
FRONTEND_URL=http://localhost:5173      <-- Should be this by default if you didn't customize the frontend configuration
```

### Run

To run:

```
flask run
```

...and the server should now be running! Remember to update your frontend's .env file as well 😄