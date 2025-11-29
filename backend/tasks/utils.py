from datetime import date

def calculate_priority(task, all_tasks, weight_urgency=0.4, weight_importance=0.3, weight_effort=0.2, weight_dependencies=0.1):
    """
    Calculates a priority score for a task.
    """

    # URGENCY: days until due (past due = max score)
    today = date.today()
    days_until_due = (task.due_date - today).days
    if days_until_due < 0:
        urgency_score = 1.0  # past due, highest urgency
    else:
        urgency_score = 1 / (days_until_due + 1)  # closer due date = higher score

    # IMPORTANCE: scale 1-10
    importance_score = task.importance / 10

    # EFFORT: less effort = higher score
    effort_score = 1 / (task.estimated_hours + 1)

    # DEPENDENCIES: if other tasks depend on this task
    dependent_count = sum([1 for t in all_tasks if task in t.dependencies.all()])
    max_dependents = max(1, len(all_tasks))
    dependencies_score = dependent_count / max_dependents

    # Weighted sum
    score = (weight_urgency * urgency_score +
             weight_importance * importance_score +
             weight_effort * effort_score +
             weight_dependencies * dependencies_score)
    return round(score, 4)
