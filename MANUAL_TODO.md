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

## 3. Publish and submit

This folder is not a Git repository and has no configured remote or branch. To obtain public file URLs, place the reviewed project files in the intended **existing public GitHub repository**. Do not create a repository, change visibility, or add a guessed remote as part of this task.

Once working in that intended checkout, first verify its status, remote, and branch. Stage only the reviewed project files, inspect the staged diff, then push to the already configured remote and intended branch:

```powershell
git status --short --branch
git branch --show-current
git remote -v
git add -- .gitignore README.md requirements.txt manage.py config onlinecourse answer.md MANUAL_TODO.md CODEX_COMPLETION_REPORT.md
git diff --cached --stat
git diff --cached
git commit -m "Complete Django online course final project"
git push -u <configured-remote> <intended-branch>
```

Replace the final placeholders only with values confirmed by Git. Do not force-push. After publishing, verify all six file URLs in `answer.md` while signed out or in a private browser window and replace the pending entries with those verified links. Upload the answers and both screenshots to the course assignment.
