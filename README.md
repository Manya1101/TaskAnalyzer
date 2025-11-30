# Smart Task Analyzer

## Setup Instructions
1. Clone the repository: `git clone https://github.com/Manya1101/TaskAnalyzer'
2. Navigate to the backend: `cd backend`
3. Create a virtual environment: `python -m venv venv`
4. Activate venv:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Apply migrations: `python manage.py migrate`
7. Run server: `python manage.py runserver`
8. Open `frontend/index.html` in your browser to use the interface.

## Algorithm Explanation
The Smart Task Analyzer calculates a **priority score** for each task using:
- **Urgency**: Tasks due sooner have higher weight.
- **Importance**: User-provided rating (1–10 scale).
- **Effort**: Tasks requiring fewer hours get a boost.
- **Dependencies**: Tasks that block other tasks rank higher.
The algorithm balances these factors using weighted contributions. Users can also select alternate strategies:
- **Fastest Wins**: Prioritize tasks with low estimated hours.
- **High Impact**: Prioritize importance over all else.
- **Deadline Driven**: Prioritize tasks due soonest.

## Design Decisions
- Used Django REST Framework for clean API design.
- Dependencies stored as many-to-many relations.
- Score calculation is configurable via sorting strategies in the frontend.
- Simplified handling of missing data and past-due tasks.

## Time Breakdown
- Backend & API: 5 hours
- Priority algorithm design: 3 hours
- Frontend interface: 2 hours
- Testing & debugging: 3 hour

## Future Improvements
- Detect and prevent circular dependencies
- User authentication
- Persistent frontend storage with localStorage or DB
