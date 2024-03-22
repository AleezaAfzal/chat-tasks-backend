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

Add in the URLs of your frontend and database, your OpenAI API key and the name of the database you wish your data to be stored in:

```.env
OPENAI_API_KEY=api_key_here
FRONTEND_URL=http://localhost:5173      <-- Should be this by default if you didn't customize the frontend configuration
DATABASE_URL=mongodb_url_here
DATABASE_NAME=database_name_here        <-- Name of the database within the mongodb cluster that DATABASE_URL points to
```

### Run

To run:

```
flask run
```

...and the server should now be running! Remember to update your frontend's .env file as well 😄

### Retrieving Data from the Database

For (hopefully obvious) security reasons (i.e. no authentication implementation), there is no way to fetch the contents of the database using this proxy API.

Once you are done with collecting data, you can use the `pymongo` library (included in `requirements.txt`) in a separate script (such as in an Jupyter notebook) to pull the contents of the database.

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