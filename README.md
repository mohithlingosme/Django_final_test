# Django OnlineCourse

A Django 5.2 project for browsing courses and lessons, authoring lesson exams in Django Admin, and recording authenticated student attempts.

## Local setup

From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the course list and `http://127.0.0.1:8000/admin/` to manage course data. The local default `SECRET_KEY` is development-only; set `DJANGO_SECRET_KEY` to a secure environment value before deployment.

## Creating course and exam data

1. In Admin, create a Course and add its Lessons using the course's inline.
2. Open each Lesson and add Questions using the lesson's inline.
3. Open each Question and add its Choices. Mark the correct choice(s) using **Is correct**.
4. Set the lesson's pass percentage. Students must sign in to submit an exam and view their own results.

The exam score is calculated on the server from the saved correct-choice flags. A `Submission` stores the attempt score and pass-mark snapshot; related `Answer` rows store each selected choice and its evaluated correctness.

## Checks

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Bootstrap 5.3.3 styling is loaded from jsDelivr by the base template.
