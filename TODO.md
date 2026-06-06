# TODO

## UI -> Backend integration
- [x] Update backend to serve existing `frontend/index.html` at `GET /`.
- [x] Mount `frontend/` as static files so `script.js` loads correctly.
- [x] Remove/replace the old inline HTML from `app/api/routes.py`.

- [x] Verify `/api/chat` and `/api/pdf/ask` remain compatible with the frontend requests.
- [x] Run `uvicorn app.main:app --reload --port 8000` and test in browser.


