# Intern Activity Tracker

This is a 3-day project I built, where I started with basic Python and ended up building a full FastAPI web application. The idea was to track interns — their daily hours, tasks, status, and overall stats.

## What it does

- Add a new intern
- Log daily activity (hours + task) for an intern
- Update an intern's status (Active / Inactive / Completed)
- View a summary for one intern (total hours, average hours, task history)
- View overall statistics across all interns (who's active, average hours, top performer)

All data gets saved to a JSON file (`intern_data.json`) so it persists even after the server restarts.

---

## Day 1 — Just Python, no APIs yet

Started simple — just a single `Intern` class in plain Python, no web stuff at all. Goal was to get comfortable with OOP basics before jumping into anything bigger.

What I did:
- Made an `Intern` class with `name`, `role`, `daily_hours`, `daily_tasks`
- Took input from the user for intern details, and made sure to clean it up (strip extra spaces, fix casing) before storing
- Built a loop that asks for hours worked and task done, for however many days I want to log
- Added validation so if someone types something that's not a number for hours, it doesn't crash — just skips that entry using try/except
- Wrote functions to calculate total hours, average hours, and print a summary
- Saved the intern data to a JSON file and read it back just to check it actually worked
- Printed a clean summary at the end

Basically this was just to get the logic right before worrying about multiple interns or an API.

## Day 2 — Multiple interns, still just console

Day 2 was about scaling it up from one intern to many, and adding a menu so I could actually interact with the program instead of just running it top to bottom.

What I did:
- Added `intern_id` and `status` fields to the Intern class (status starts as "Active")
- Built an "Add Intern" option — generates an ID like INT001, INT002 automatically, saves to the list and then to JSON
- Built "Add Daily Activity" — but only lets you log hours if the intern's status is Active. If they're Inactive or Completed, it blocks it
- Added a way to update status (Active → Inactive → Completed)
- Built "View Summary" for a single intern — shows total/avg hours and their task history
- Built "Overall Statistics" — total interns, how many are active, average hours across everyone, and who the top performer is
- Wrapped it all in a menu so I could pick options 1-6 instead of running separate scripts

This was still a console app, no web/API stuff yet, just to nail the logic for multiple interns and statuses before converting it.

## Day 3 — Converted to FastAPI

This is where it became an actual web API. Converted everything from Day 2 into FastAPI endpoints.

What I did:
- Set up a FastAPI app in `main.py`, ran it with `uvicorn main:app --reload`
- Checked it worked by hitting `http://127.0.0.1:8000` and opening Swagger docs at `/docs`
- Made the JSON read/write functions async (`await`) instead of blocking, so the server doesn't freeze up on file operations
- Built the endpoints:
  - `POST /interns` — add an intern (validated using a Pydantic model)
  - `POST /interns/{intern_id}/activity` — log hours + task for an intern
  - `PATCH /interns/{intern_id}/status` — update status
  - `GET /interns/{intern_id}` — get one intern's summary
  - `GET /statistics` — get overall stats
- Tested everything on Swagger UI — tried valid and invalid inputs (missing fields, negative hours, logging activity for an Inactive intern, hitting an intern ID that doesn't exist)
- Opened two browser tabs and fired requests at the same time just to actually see the async behavior working instead of the server blocking one request while handling another

## Restructuring (after Day 3)

Once Day 3 was done, my lead reviewed it and asked me to split everything out of the single `main.py` into a proper folder structure instead of having all the logic and endpoints crammed into one file. So I reorganized it into:

```
Intern Activity Tracker/
├── main.py                       # just creates the app and plugs in the routers
├── schemas.py                    # the Pydantic models
├── database.py                   # async read/write to the JSON file
├── utilities.py                       # small helper functions (find_intern, generate_intern_id)
├── routers/
│   ├── interns.py                # only the endpoint definitions, no logic
│   └── statistics.py             # same, just the /statistics endpoint
└── services/
    ├── interns_service.py        # actual logic for the intern endpoints
    └── statistics_service.py     # actual logic for the statistics endpoint
```

The routers just call the matching function in `services/` — no logic inside the route functions themselves anymore. I re-tested everything after moving the code around to make sure the responses were exactly the same as before, and they were.

---

## How to run it

```bash
pip install fastapi uvicorn aiofiles
python main.py
```

Then go to `http://127.0.0.1:8000/docs` to test the endpoints from Swagger.

## A few notes to self

- `intern_data.json` gets created automatically the first time you add an intern, don't need to make it manually
- IDs are just based on how many interns are already in the list (`INT001`, `INT002`...) — not the most bulletproof way to do it but works fine for this
- Still need to be careful that this doesn't handle multiple people writing to the JSON file at the exact same time — fine for now since it's a small project, but wouldn't scale to a real production system with a proper database
