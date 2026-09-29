# SkillSwap Production-Level Improvement Plan

This project already has a good student-project foundation: users can register, create profiles, select skills to teach or learn, search other users, and send exchange requests. To impress a company, the project should now look more complete, safer, cleaner, and easier to run.

The goal is not to make it huge. The goal is to make it look like a serious Django product built with professional habits.

## Current Project Summary

- Framework: Django
- Main app: `skills`
- API app: `drf_app`
- Main features: authentication, profile management, skill search, exchange requests, custom admin dashboard
- Deployment config: `render.yaml`
- Database: SQLite locally, PostgreSQL on Render through `DATABASE_URL`
- Static files: WhiteNoise configured

## Highest Priority Changes

### 1. Clean the Repository Structure

The project currently has a local `venv/` folder beside the Django app. A company should not see virtual environment files in the repository.

Recommended changes:

- Add a proper `.gitignore`.
- Exclude `venv/`, `.venv/`, `db.sqlite3`, `__pycache__/`, `.env`, `staticfiles/`, and editor files.
- Keep only source code, templates, migrations, requirements, README, and deploy files.
- Rename `skills/Templates` to the conventional Django path `skills/templates/skills/`.

Why this matters:

Companies expect clean repositories. A repo containing environment files looks unfinished and inexperienced.

### 2. Improve Settings for Real Production

`SkillSwap/settings.py` is partly production-ready, but it should be split and tightened.

Recommended changes:

- Use environment variables for all secrets and deployment settings.
- Fail loudly in production if `DJANGO_SECRET_KEY` is missing.
- Add `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and `LOGOUT_REDIRECT_URL`.
- Add `SECURE_HSTS_INCLUDE_SUBDOMAINS` and `SECURE_HSTS_PRELOAD` for production.
- Add proper email host settings or remove incomplete mail config.
- Move development and production settings into separate files if the project grows.

Why this matters:

Secure configuration is one of the first things reviewers notice in Django projects.

### 3. Replace Manual Form Handling With Django Forms

Most forms are handled directly with `request.POST`. This works, but it is not ideal for validation, error display, or maintainability.

Recommended changes:

- Create `forms.py` inside the `skills` app.
- Add forms for registration, login, profile update, exchange request, and admin user editing.
- Use Django's password validators instead of only checking password length.
- Show field-level validation errors in templates.

Why this matters:

Professional Django projects usually rely on forms or serializers for validation instead of manually reading every POST value.

### 4. Fix Dangerous GET Actions

Some important actions, such as accepting, rejecting, and deleting, are exposed through normal links and can be triggered by GET requests.

Recommended changes:

- Make accept request, reject request, and delete user actions POST-only.
- Add confirmation screens or modal confirmation for delete actions.
- Use `@require_POST` for state-changing views.

Why this matters:

GET requests should not change data. This is a common web security and correctness issue.

### 5. Improve the Data Models

The current models are simple and good for a first version, but they need stronger rules.

Recommended changes:

- Add `unique=True` to `Skill.name`.
- Add `created_at` and `updated_at` fields to `Profile`.
- Replace request status text with choices, for example `PENDING`, `ACCEPTED`, `REJECTED`.
- Add a database constraint to prevent duplicate pending requests from the same sender to the same receiver.
- Consider preventing users from teaching and learning the same skill unless that is intentional.

Why this matters:

Database constraints protect the app even if a future view or API has a bug.

### 6. Build a More Complete User Experience

The app should feel like a real product, not just a set of forms.

Recommended changes:

- Add a polished landing page that explains SkillSwap before login.
- Add a user profile detail page.
- Add empty states for no skills, no search results, and no requests.
- Add success and error messages after important actions.
- Add profile completion progress.
- Add skill category filters.
- Add a better search that can search by skill, username, name, and bio.
- Hide the current user from search results.
- Show accepted connections separately from pending requests.

Why this matters:

Companies are impressed when the app feels thought-through from the user's point of view.

### 7. Move CSS Into Static Files

Every template currently has inline CSS. This creates duplication and makes the UI harder to maintain.

Recommended changes:

- Create `skills/static/skills/css/base.css`.
- Create shared layout styles, button styles, card styles, form styles, and navigation styles.
- Use `{% load static %}` in templates.
- Create a base template such as `base.html`.
- Make pages extend `base.html`.

Why this matters:

A shared layout and stylesheet make the project look organized and production-minded.

### 8. Add Tests

The test files currently do not cover the real behavior.

Recommended test coverage:

- User registration works.
- Duplicate username is rejected.
- Login and logout work.
- Profile creation and update work.
- Skill search returns matching users.
- Users cannot send requests to themselves.
- Duplicate pending requests are blocked.
- Only the receiver can accept or reject a request.
- Admin-only pages reject normal users.
- Delete user cannot delete staff or superusers.

Why this matters:

Tests are one of the strongest signals that a student can write maintainable software.

### 9. Clean or Complete the API App

The `drf_app` currently looks unfinished. It has commented code and a serializer for an `Info` model, but the model is not clearly connected to the SkillSwap product.

Recommended options:

- Remove `drf_app` if it is not needed.
- Or turn it into a real API for SkillSwap.

If keeping the API, add endpoints for:

- List skills
- List searchable profiles
- View a profile
- Send an exchange request
- List sent and received requests
- Accept or reject requests

Why this matters:

Unfinished code makes the project look less polished. A small complete API is better than a large incomplete one.

### 10. Improve the README

The README is already useful, but it can become portfolio-ready.

Recommended additions:

- Add screenshots.
- Add a short problem statement.
- Add a feature table.
- Add tech stack.
- Add project architecture.
- Add environment variable documentation.
- Add demo login credentials for reviewers.
- Add deployment URL after hosting.
- Add test command and coverage notes.
- Add future improvements.

Why this matters:

Many recruiters and engineers read the README before opening the code.

## Suggested Feature Upgrades

These features would make SkillSwap feel more like a real product:

- User profile photos.
- Skill categories such as programming, design, language, music, business.
- Request messages with conversation history.
- Accepted connection list.
- Meeting availability or preferred learning mode.
- Ratings or testimonials after a skill exchange.
- Notifications for new requests.
- Admin management for skills.
- Public profile sharing.
- Pagination for users and requests.

Do not build all of these at once. Pick two or three and finish them well.

## Suggested Technical Upgrades

- Add `ruff` or `flake8` for code quality.
- Add `black` for formatting.
- Add `pytest-django` or improve Django's built-in tests.
- Add GitHub Actions for automated tests.
- Add type hints in service/helper functions.
- Add `pre-commit` hooks.
- Add seed data command for demo users and skills.
- Add proper logging instead of only custom exception middleware.
- Use Django messages framework for user feedback.

## Suggested Folder Structure

```text
skillswap/
├── manage.py
├── requirements.txt
├── README.md
├── render.yaml
├── .env.example
├── .gitignore
├── SkillSwap/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── skills/
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    ├── migrations/
    ├── static/
    │   └── skills/
    │       └── css/
    │           └── base.css
    └── templates/
        └── skills/
            ├── base.html
            ├── landing.html
            ├── login.html
            ├── register.html
            ├── dashboard.html
            ├── profile_form.html
            ├── profile_detail.html
            ├── find_skills.html
            └── requests.html
```

## Recommended Implementation Roadmap

### Phase 1: Clean and Stabilize

- Add `.gitignore`.
- Remove virtual environment files from version control.
- Move inline CSS to static files.
- Add `base.html`.
- Clean commented code.
- Remove or complete `drf_app`.

Expected result:

The repo looks clean and easy to understand.

### Phase 2: Security and Correctness

- Convert delete, accept, and reject actions to POST-only.
- Add model choices and constraints.
- Improve registration and password validation.
- Add success and error messages.
- Make settings stricter for production.

Expected result:

The app behaves more safely and professionally.

### Phase 3: Product Polish

- Add landing page.
- Add profile detail page.
- Improve search results.
- Add empty states.
- Add better dashboard cards.
- Add screenshots to README.

Expected result:

The project feels like a real app someone could use.

### Phase 4: Testing and Deployment Proof

- Add tests for core flows.
- Add GitHub Actions.
- Add demo data command.
- Deploy on Render.
- Add live demo link and demo credentials to README.

Expected result:

The student can confidently show the project to a company.

## Minimum Changes Before Showing to a Company

If time is short, complete these first:

1. Add `.gitignore` and remove `venv/` from the repo.
2. Add shared `base.html` and static CSS.
3. Fix POST-only actions for delete, accept, and reject.
4. Add proper Django forms and validation.
5. Add tests for registration, profile update, search, and requests.
6. Clean or remove the unfinished `drf_app`.
7. Improve README with screenshots and deployment instructions.
8. Deploy the project and include the live link.

## Final Quality Checklist

- App runs from a fresh clone using README steps.
- No virtual environment or database file is committed.
- No secret key is committed.
- `DEBUG=False` works in deployment.
- All forms validate data correctly.
- State-changing actions use POST.
- Core user flows have tests.
- UI is consistent across pages.
- README has screenshots and a live demo link.
- The project has a clear story: what problem it solves, who it helps, and what the student built.

## Best Portfolio Pitch

Use this project as a skill-exchange platform for students:

"SkillSwap helps students find classmates who can teach skills they want to learn. Users create profiles, list skills they can teach and want to learn, search matching profiles, and send exchange requests. I built authentication, profile management, search, request workflows, admin management, deployment configuration, and tests."

That pitch is simple, clear, and company-friendly.
