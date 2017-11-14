# Live Counter

Server implementation and API for a counter with live updates. POST to increment. GET to listen for updates (server-sent events). This project uses Fastly and Fanout for high scale. See [livecounter.org](http://livecounter.org/)

## Setup

Install dependencies:

```sh
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

Also be sure you have Redis installed, which the main server process uses to communicate with the publisher process.

Ensure you have accounts with Fastly and Fanout Cloud, and set up the same domain in both systems. Additionally, create a Fastly API key. Then, create a `.env` file with the following environment variables:

```
FASTLY_API_KEY={api-key}
FASTLY_DOMAIN={domain-name}
GRIP_URL=http://api.fanout.io/realm/{realm-id}?iss={realm-id}&key=base64:{realm-key}
```

You can also set `DATABASE_URL` to point to a database. If not set, sqlite will be used.

Create database tables:

```sh
python manage.py migrate
```

Create a counter object:

```py
from livecounter.models import Counter
c = Counter(name='foo')
c.save()
```

## Running

Run the main server (either using `python manage.py runserver` or a webserver with `server/wsgi.py`).

Also, run the publisher command (`python manage.py publisher`, either in another terminal or as a background service).

Point the domain CNAME at Fanout Cloud. Configure the Fanout Cloud domain to proxy traffic to Fastly. Configure Fastly to point traffic to this server.
