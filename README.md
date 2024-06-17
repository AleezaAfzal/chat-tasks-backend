# Chat + Tasks (Proxy Server)

The backend for our online study application. Handles messaging with GPT-4 and saving responses to the database. You can find the participant-facing application [here](https://github.com/aaltoengpsy/chat-tasks-frontend).

- [Running Locally](#running-locally)

  - [Setup](#setup)

  - [Run](#run)

- [Deploying Online](#deploying-online)

- [Retrieving Data from the Database](#retrieving-data-from-the-database)

## Overview

The repository features a Flask server (`app.py`) offering three endpoints: `/chat`, `/save` and `/check_participation`. The first of these is used to communicate with the OpenAI API to complete ChatGPT prompts (including pre-encoded images, if included) entered by participants using the study's frontend. The latter two are offered for checking participation and dumping participation data to an attached MongoDB database.

Participation data is only saved if the supplied participant ID does not already exist in the database. `database_helpers.py` contains helper functions that use the `pymongo` librabry to connect to the database as well as to insert new entries and check for existing entries with a given identifier.

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

Add in the URLs of your frontend and database, your OpenAI API key, GPT parametersm the name of the database you wish your data to be stored in and the completion code & url for your study.

```.env
OPENAI_API_KEY=api_key_here
GPT_VERSION=gpt-4-turbo
GPT_TOKEN_LIMIT=1000                     
FRONTEND_URL=frontend_url_here          # http://localhost:5173 by default
DATABASE_URL=mongodb_url_here
DATABASE_NAME=database_name_here        # Name of the database within the cluster that DATABASE_URL points to
PROLIFIC_CODE=prolific_return_code_here # Completion code to be displayed to the participant (not necessarily prolific)
PROLIFIC_URL=prolific_return_url_here   # Completion url to be displayed to the participant (not necessarily prolific)
```

[Install redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/) locally; we need this for [queue management](#queue-management).

### Run

To run:

```
flask run
```

...and the server should now be running! Remember to update your frontend's .env file as well so that it points to the address of the server! 😄

## Queue Management

Because GPT calls can take long to process, they should be run as a background job to avoid surpassing the 30-second Heroku dyno timeout. This project uses [RQ](https://python-rq.org/) to queue API calls.

## Deploying Online

The repository should be deployable to e.g. [Heroku](https://www.heroku.com/) or [DigitalOcean's App Platform](https://www.digitalocean.com/products/app-platform) directly from GitHub. Create a project, connect your GitHub and select the repository. Remember to set your environment variables ("Config Vars" on Heroku)! Remember to update your frontend deployment's environment variables to point to the address of the deployed server.

## Retrieving Data from the Database

For (hopefully obvious) security reasons (i.e. no authentication implementation), there is no way to fetch the contents of the database using this proxy API.

Once you are done collecting data for your study, you can use the `pymongo` library (included in `requirements.txt`) in a separate script (such as in an Jupyter notebook) to pull the contents of the database.

```python
client = MongoClient(DATABASE_URL)
db = client[DATABASE_NAME]             
collection = db[COLLECTION_NAME]

items = collection.find()           # Fetches all items from the specified collection
```

`items` is be *iterable*, so you will need to iterate through it to access the contents:

```python
for item in items:
    print(item)
```

`items` is also *consumed* when it's iterated upon, so to access its contents again, you will need to either fetch it again:

```python
items = collection.find()
```

**OR**, you can clone the contents to a separate variable when you fetch the items the first time:

```python
items_consumable = collection.find()
items_to_reuse = items_consumable.clone()

for item in items_to_reuse:
    # DO STUFF HERE
    pass
```

Alternatively, you can use the [mongoexport tool](https://www.mongodb.com/docs/database-tools/mongoexport/) to extract the contents of the database.