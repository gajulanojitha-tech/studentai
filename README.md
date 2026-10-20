# StudentAI – AI Learning Companion
Developed by Gajula Nojitha

Personal AI tutor for Grades 6–12 (Math, Physics, Chemistry): text, voice and photo questions, 7 languages,
offline lessons, practice, revision, formula sheet, periodic table and 3D molecules.

## Run on your computer (no VS Code needed)
1. Right-click `config.txt` → Open with → **Notepad**. Paste your Gemini key after `GEMINI_API_KEY=` and save.
   (Free key: https://aistudio.google.com/apikey. Optional backup key from https://console.groq.com goes after `GROQ_API_KEY=`.)
2. Double-click **start.bat**. Your browser opens the site. Keep the black window open; close it to stop.
3. First time only: if Windows says Python is missing, install it from python.org and tick "Add Python to PATH".

The AI key stays in `config.txt` on the server side. It is never sent to the browser.
Never upload `config.txt` to GitHub (the included `.gitignore` already skips it).

## Put it online (the key stays on the server)
GitHub Pages cannot run a backend. Use Vercel or Netlify (free):
1. Upload this folder to a GitHub repository (without config.txt).
2. Import the repository in Vercel or Netlify.
3. In the host's Environment variables add `GEMINI_API_KEY` (optional `GROQ_API_KEY`, `GEMINI_MODEL`).
4. Deploy. `api/chat.js` (Vercel) or `netlify/functions/chat.js` + `netlify.toml` (Netlify) do the same job as `server.py`.
Each visitor is limited to 20 requests per minute.

## Structure
- `index.html`, `css/style.css`: landing page and tutor layout
- `js/app.js`, `js/features.js`: tutor, library, practice, tools, progress, accessibility
- `js/content.js`, `js/data.js`: syllabus, offline notes, solver, periodic table, formulas, molecules
- `js/api.js`: talks only to `/api/chat`
- `server.py`: local backend (standard library only), `start.bat`: double-click launcher
- `finetune/`: LoRA training recipe and before/after accuracy script

## Offline
Answer chain: saved answer → AI (Gemini, then Groq backup) → on-device AI (optional) → solver, saved lessons, your notes, built-in notes.
In the Library tab, press "Download all for offline" while online.

## Limits
AI can make mistakes; lessons should be checked by a teacher. Translated labels should be reviewed by native speakers.
The leaderboard and class dashboard need a database and are not included.
