# Completion Report

## Summary

The supplied folder initially contained only the assignment prompt and submission notes; it had no Django source, Git metadata, or remote. After the user clarified that no checkout path was available and asked for a project to be created, a new single-project Django OnlineCourse implementation was scaffolded here. It is not a modification of an existing checkout.

## Implementation

- Created a Django 5.2 project (`config`) and `onlinecourse` app, with requirements, README, and ignore rules for the local virtual environment, database, caches, and `.env` files.
- Added `Course`, `Lesson`, `Question`, and `Choice`; `Submission` records a student's score/pass snapshot, while related `Answer` rows preserve each selected choice and server-evaluated correctness.
- Added authenticated GET/POST exam handling with per-question choice validation, CSRF protection, transactional persistence, score calculation from stored `Choice.is_correct`, pass-mark evaluation, and owner-only result retrieval.
- Added namespaced course/exam/result URLs, standard Django login/logout routes, Bootstrap 5.3 templates, an empty-course lesson state, and admin registration/inlines.
- The rubric's “seven imported classes/modules” identities were not supplied by lab materials. The implementation uses seven meaningful imported names in `admin.py`: Django's `admin` module plus the six directly used app models (`Answer`, `Choice`, `Course`, `Lesson`, `Question`, `Submission`). No unused imports or dummy classes were added.
- The pass criterion is a per-lesson percentage (default 70%); the attempt stores the pass threshold at submission time. Percentage scores are whole-number percentages rounded down.

## Files created or updated

Project files: `.gitignore`, `README.md`, `requirements.txt`, `manage.py`, `config/`, and `onlinecourse/` (models, admin, forms, views, URLs, tests, initial migration, and templates).

Submission files: `answer.md`, `MANUAL_TODO.md`, and this report.

## Environment and validation

- Python 3.12.10 was initially configured, but its standard-library `warnings.py` was empty and prevented `venv` creation. Python 3.11.9 worked; the project-local `.venv` was created with it.
- Installed Django 5.2.19 in `.venv` with `.venv\Scripts\python.exe -m pip install 'Django>=5.2,<5.3'`.
- `.venv\Scripts\python.exe manage.py makemigrations onlinecourse` — created `onlinecourse/migrations/0001_initial.py`.
- `.venv\Scripts\python.exe manage.py check` — passed; no issues.
- `.venv\Scripts\python.exe manage.py makemigrations --check --dry-run` — passed; no changes detected.
- `.venv\Scripts\python.exe manage.py test` — passed; 7 tests.
- `.venv\Scripts\python.exe manage.py test onlinecourse` — passed; 7 tests, including exam score/pass behavior, invalid and missing answers, CSRF enforcement, result privacy, login routing, empty lesson display, and both admin app labels.
- `.venv\Scripts\python.exe manage.py migrate --noinput` — passed; Django and OnlineCourse migrations applied to the local SQLite database. `db.sqlite3` is ignored.
- VS Code diagnostics for the changed Python files — no errors found.
- No separate linter or formatter was configured/documented.

## Screenshots and demonstration data

- Captured genuine browser screenshots of the local Django Admin index (`03-admin-site.png`) and a student's successful exam result (`07-final.png`).
- Verified in the running browser that the admin index showed both **Authentication and Authorization** and **OnlineCourse**.
- The result screenshot came from the normal login and exam submission flow, with three saved questions, server-checked stored correct answers, and a calculated 100% score against the 70% lesson pass threshold.
- Screenshot sizes: `03-admin-site.png` 27,570 bytes; `07-final.png` 35,834 bytes. No image was drawn or edited.
- Local demonstration course, lesson, questions, choices, and successful submission remain in the ignored development database. The temporary superuser was deleted, and the temporary student's password was disabled after capturing screenshots. Create your own superuser with `createsuperuser` if you need to use the local admin.

## GitHub publishing

- Published to the user-provided public repository `https://github.com/mohithlingosme/Django_final_test` on branch `main`.
- The initial project commit was `ab6057e07700dcd9e22927110ee8e168c0c2f21c`; answer sheets were updated after push and verified public.
- The five code file URLs are recorded in the root `answer.md` and `Submission/answer.md`. Each source-file page returned HTTP 200 to unauthenticated `curl.exe` requests.
- `main` tracks `origin/main`. The supplied workspace also contains untracked root screenshots and `CODEX_PROMPT.md`; those were intentionally not committed. Submission screenshot copies are committed under `Submission/`.
- User must still upload `Submission/03-admin-site.png`, `Submission/07-final.png`, and the answers to the course assignment.
