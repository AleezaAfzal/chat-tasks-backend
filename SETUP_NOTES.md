# Setup Notes: Running and Deploying the Aalto Chat-Tasks Study Interface

> **About this fork.** This repository is a fork of [`aaltoengpsy/chat-tasks-backend`](https://github.com/aaltoengpsy/chat-tasks-backend). I forked it **for learning and practice only**. I did not modify the original code, and no real participants or real study data were involved. These notes document how I set up the system locally and deployed it online as a practice exercise. All credit for the software goes to the original authors at Aalto University.
>
> **No secrets are included here.** Every password, key, connection string and web address below is a placeholder. The practice deployment has been shut down and its database deleted.

Practice date: October 2026.

---

## 1. What this project is

The two repositories together form a **participant-facing web interface for online behavioural research**. They were built for a study on how people judge their own performance (metacognition) when solving logical-reasoning questions, with and without access to an AI chat assistant. The research paper is *"AI Makes You Smarter but None the Wiser: The Disconnect Between Performance and Metacognition"*. See the original repository README for the full citation.

| Part | Repository | Role |
|---|---|---|
| Frontend | [`aaltoengpsy/interface-frontend`](https://github.com/aaltoengpsy/interface-frontend) | The website participants see: questions, scales, optional chat window |
| Backend | [`aaltoengpsy/chat-tasks-backend`](https://github.com/aaltoengpsy/chat-tasks-backend) (this fork) | Server that saves data and, if enabled, relays chat messages to OpenAI |
| Database | MongoDB Atlas (free tier) | Stores participant records |

**Not tested:** the AI chat feature. I ran the `no-ai` condition only, so no OpenAI API key or paid service was used.

### Architecture

```
Participant's browser (React frontend, hosted as static files)
        │
        ▼
Flask backend (gunicorn)  ──►  MongoDB Atlas  (saved answers)
        │
        └──► Redis queue + worker ──► OpenAI API   (chat only, not used here)
```

### What the backend exposes

| Route | Purpose |
|---|---|
| `POST /check_participation` | Checks whether a participant ID already exists (204 = new, 302 = already used) |
| `POST /save` | Saves the participant's record (the ID is the unique `_id`, so duplicates are rejected) |
| `POST /chat`, `POST /check_response` | Chat via a Redis job queue (not used in `no-ai`) |

Opening the backend address in a browser shows **"Not Found"**. That is normal: the server has no home page.

---

## 2. Tools needed (Windows)

| Tool | Notes |
|---|---|
| Git | For `git clone` |
| **Python 3.12** | **Not 3.13 or newer.** `requirements.txt` pins early-2024 package versions (e.g. `pydantic_core 2.16.3`) with no prebuilt wheels for newer Python. Python versions install side by side, so adding 3.12 does not remove another version. |
| Node.js (LTS) | For the frontend (`npm`) |
| VS Code |  |
| MongoDB Atlas account | M0 cluster |

I used Command Prompt (not PowerShell) in the VS Code terminal to avoid script-execution restrictions when activating the virtual environment.

---

## 3. Database setup (MongoDB Atlas)

1. Create a free **M0** cluster.
2. **Database Access:** create a database user with a username and a password using **letters and numbers only** (symbols such as `@ : / ?` break the connection string).
3. **Network Access:** add `0.0.0.0/0` ("allow from anywhere"). This was acceptable for practice only. For a real study, restrict it.
4. **Connect → Drivers:** copy the connection string and replace the `<password>` placeholder, including the `<` `>` brackets, with the real password.
5. The database and the `data` collection are created automatically on the first save.

---

## 4. Backend: run locally

```bash
git clone https://github.com/YOUR-USERNAME/chat-tasks-backend.git
cd chat-tasks-backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a file named exactly `.env` (already listed in `.gitignore`, so it is never uploaded):

```
OPENAI_API_KEY=sk-placeholder-not-used
GPT_VERSION=gpt-4o-mini
GPT_TOKEN_LIMIT=1000
FRONTEND_URL=http://localhost:5173
DATABASE_URL=YOUR_ATLAS_CONNECTION_STRING
DATABASE_NAME=yourdatabasename
PROLIFIC_CODE=TESTCODE
PROLIFIC_URL=https://app.prolific.com
```

Start the server:

```bash
flask run
```

It listens on `http://127.0.0.1:5000`.

### Why the AI settings are needed even without the chat

I read the backend source to check what could be skipped:

- `chat_helpers.py` creates the OpenAI client **when the server starts**. It fails if `OPENAI_API_KEY` is missing, and `int(os.getenv('GPT_TOKEN_LIMIT'))` fails if that is missing. A **dummy key** is enough, because the API is never called unless someone uses the chat.
- `worker.py` creates the Redis connection lazily, so the server starts without Redis. `/save` and `/check_participation` never touch Redis.
- Therefore, for the `no-ai` condition, **Redis, the worker and OpenAI are not needed**.

### Variable reference

| Variable | Meaning |
|---|---|
| `FRONTEND_URL` | The **only** website address allowed to call the backend (CORS). Must match exactly: same scheme, no trailing slash. Only one value is accepted. |
| `DATABASE_URL` | Atlas connection string |
| `DATABASE_NAME` | Any name; created automatically |
| `PROLIFIC_CODE`, `PROLIFIC_URL` | Shown to participants after saving (Prolific is a participant-recruitment platform) |

Optional connection test (`test_db.py`, then delete it):

```python
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("DATABASE_URL"), serverSelectionTimeoutMS=8000)
print(client.admin.command("ping"))
```

Expected output: `{'ok': 1.0}`.

---

## 5. Frontend: run locally

```bash
git clone https://github.com/aaltoengpsy/interface-frontend.git
cd interface-frontend
npm install
git submodule init
git submodule update
```

The submodule (`taskParser`) is the helper that turns the text question files into pages.

Create `.env` in the **project root** (next to `package.json`):

```
VITE_PROXY_URL=http://127.0.0.1:5000
VITE_PCTP_CONDITION=no-ai
VITE_DEV_MODE=false
```

(The original repository documents more variables, such as chat page range, image uploads and the attention check. See its README. I left those at the original values.)

Start it:

```bash
npm run dev
```

Open **`http://localhost:5173`**, exactly as written. The backend only allows that origin.

Both programs must run at the same time (two terminal windows). Closing VS Code or the terminal stops them.

### Notes

- **`.env` changes need a restart** of `npm run dev`. Vite reads the file only at startup.
- `VITE_PROXY_URL` is baked into the website **at build time**.
- **No trailing slash** on `VITE_PROXY_URL`. The site adds `/check_participation` itself, and a trailing slash produced `//check_participation`, which failed.

---

## 6. How the ID screen works

I read `App.jsx` and `dbService.js`:

- The ID must be **at least 16 characters** (after trimming). Shorter input shows "Please enter your Prolific ID." *before* any request goes to the backend. (Real Prolific IDs are 24 characters.)
- With `VITE_DEV_MODE=true`, the ID check is skipped completely. Useful for quick layout testing, but it hides connection problems, because no request is made until the final save. Set it to `false` for real data collection.
- On submit, the site calls `/check_participation`. A 204 lets the participant continue; a 302 means the ID already took part; anything else shows an error.

---

## 7. Editing the questions

All content comes from a plain text file in `public/`:

| File | Used when |
|---|---|
| `no-ai_tasks.md` | `VITE_PCTP_CONDITION=no-ai` |
| `ai_tasks.md` | `VITE_PCTP_CONDITION=ai` |

Syntax (from the [taskParser README](https://github.com/aaltoengpsy/taskParser.js)):

| Symbol | Meaning |
|---|---|
| `#` | New page (text after it is the title) |
| `##`, `###` | Subheadings within a page |
| `>` | Paragraph, or a question if a `$` line follows |
| `$text`, `$number` | Free text or number input |
| `$option; A; B; C` | Multiple choice |
| `$likert; 1; 7; Low label; High label` | Rating scale |
| `$slider; 0; 100; Low label; High label` | Slider |
| `%% RANDOMIZE` … `%%` | Pages in between are shown in random order |

Example:

```md
# About You

> How old are you?

    $number

> How stressed did you feel this week?

    $likert; 1; 7; Not at all; Extremely
```

Each question needs a blank line around it and a `>` at the start. A missing `>` or blank line is the usual cause of a blank page. The saved record keeps a `sourceIndex` for each page, so randomised pages can be matched back to their original position.

After saving, refresh the browser. If the old content persists, restart `npm run dev`.

A saved record in the `data` collection contains `_id` (participant ID), `condition`, `tasks` (all pages with answers) and `messages` (chat log; empty in `no-ai`).

---

## 8. Deployment (practice)

I deployed the backend to **Render** (free tier) and the frontend to **Netlify**. Both are shut down now.

### Backend on Render

| Setting | Value |
|---|---|
| Source | Public Git repository (the fork)|
| Runtime | Python 3 |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:app` |
| Instance type | Free |
| Environment | All variables from section 4, plus `PYTHON_VERSION=3.12.3` |

- `PYTHON_VERSION` is essential, otherwise Render may choose a Python too new for the pinned packages.
- The project's `Procfile` also defines a `worker` process. It is only for the chat queue and was not used.
- Render asked for a **card for account verification**. Support documents it as a $1 authorisation that is reversed. My bank additionally charged an **international-transaction fee**, so the "free" tier cost a small amount in practice.


Quick check after deployment: the root address shows "Not Found", and `/check_participation` opened in a browser shows "Method Not Allowed". Both mean the server is alive.

### Frontend on Netlify

1. In the frontend `.env`, set `VITE_PROXY_URL` to the Render address (**no trailing slash**) and `VITE_DEV_MODE=false`.
2. Run `npm run build`. This creates the `dist` folder (the complete static website).
3. Drag the **`dist` folder** onto Netlify's manual-deploy page (a free account was enough).
4. Set `FRONTEND_URL` on Render to the Netlify address (exact, `https`, no trailing slash), and let Render redeploy.
5. To update later, rebuild and drag the new `dist` into the site's **Deploys** tab.

---

## 9. Problems I hit and how I fixed them

| Symptom | Cause | Fix |
|---|---|---|
| Console shows `POST .../undefined/check_participation` | Frontend `.env` was not read (wrong location, or no restart) | Put `.env` in the project root and restart `npm run dev` |
| "Please enter your Prolific ID" with a short test ID | ID shorter than 16 characters | Use 16+ characters |
| Everything worked in dev mode but not in normal mode | Dev mode skips the ID check and the first backend call | Test with `VITE_DEV_MODE=false` |
| `pip install` failures | Python 3.14 had no wheels for the pinned packages | Use Python 3.12 in the virtual environment |
| Backend stopped | The terminal was closed | Reactivate the venv and run `flask run` again |
| `//check_participation` in the request URL | Trailing slash in `VITE_PROXY_URL` | Remove the slash and rebuild |
| CORS error although `FRONTEND_URL` was correct | The Netlify site was set to **private**, so its responses were blocked | Make the site public. I confirmed the backend was correct first with `curl -X OPTIONS` and an `Origin` header; the response contained `access-control-allow-origin` |
| Harmless console warnings | `uncontrolled to controlled`, `favicon.ico 404`, `className false` | Ignore |

Useful backend test (replace the placeholders):

```bash
curl -i -X OPTIONS https://YOUR-BACKEND/check_participation -H "Origin: https://YOUR-SITE" -H "Access-Control-Request-Method: POST"
```

---

## 10. Before using this for a real study

This was a practice run only. A real deployment would need at least:

- **Ethics approval and a consent form** (the repository includes only examples)
- A server that does not sleep (paid tier), or a deployment only for the study period
- Network access in Atlas restricted instead of `0.0.0.0/0`
- `VITE_DEV_MODE=false`, real `PROLIFIC_CODE`/`PROLIFIC_URL`, and test records deleted
- A plan for **exporting data** (for example `mongoexport`, or Python with `pymongo`)
- A simpler tool may be better if no custom behaviour is needed. The taskParser authors themselves recommend Qualtrics, Microsoft Forms or Google Forms unless a custom interface is required.

---

## 11. Shutdown (done)

Render service deleted, Netlify site deleted, Atlas cluster terminated, local folders removed. Nothing from this practice is still running.

---

## 12. Licence and credit

- Frontend: GPL-3.0. Backend: MIT (as stated in the original repositories at the time of reading; check them for the current terms).
- Original software and research: Aalto University researchers, see the repositories above.
- This fork contains no changes to the original source code. Only this notes file was added.

## How I learned this

I had no prior experience with web deployment, databases or the tools used here. I worked through the whole process step by step with the help of **Claude** , which explained the architecture, gave setup instructions and helped me interpret errors.

Every problem listed in section 9 was something I hit myself and then debugged by reading the **browser developer console (F12)**, the terminal output and the Render logs. I tested each fix on my own setup and confirmed it worked before moving on. The troubleshooting table reflects what actually happened in my practice run.
