# Manual TODO

## 1. Start the local project (if needed)

In PowerShell, from the project root:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Use your own local admin credentials; do not put passwords in the submission. Open `http://127.0.0.1:8000/admin/`. Temporary screenshot-only logins were removed/disabled after capturing the screenshots.

## 2. Screenshot status

- [x] `03-admin-site.png` captured from the running Django Admin with both required sections visible.
- [x] `07-final.png` captured after a real authenticated exam submission using the stored correct choices; it shows Congratulations, 100%, and evaluated answers.
- Screenshots are in the project root and were not altered.

## 3. Submit the assignment

The project is published on the `main` branch of `https://github.com/mohithlingosme/Django_final_test`. The five source links are in `answer.md` and `Submission/answer.md`.

- [ ] Open each GitHub file URL while signed out or in a private browser window.
- [ ] Upload `Submission/03-admin-site.png` for Question 3.
- [ ] Upload `Submission/07-final.png` for Question 7.
- [ ] Submit the five public URLs and both screenshots in the course assignment.
