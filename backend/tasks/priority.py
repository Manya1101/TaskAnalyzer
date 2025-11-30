from datetime import date

def calculate_priority(task, all_tasks, visited=None):
    """
    Calculate priority score for a task.
    - Urgency: Tasks due sooner get higher score
    - Importance: 1-10 scale
    - Effort: lower hours = slightly higher score
    - Dependencies: tasks blocking others get higher score
    """

    if visited is None:
        visited = set()

    # Detect circular dependency
    if task.id in visited:
        return 0  # If cycle, set score to 0
    visited.add(task.id)

    # Urgency factor
    days_left = (task.due_date - date.today()).days
    if days_left < 0:
        urgency_score = 1.0  # Past due, max urgency
    else:
        urgency_score = 1 / (days_left + 1)  # Sooner due → higher score

    # Effort factor (lower estimated_hours slightly increases priority)
    effort_score = 1 / (task.estimated_hours + 1)

    # Importance factor (1-10 scale normalized)
    importance_score = task.importance / 10

    # Dependency factor: tasks blocking others get higher priority
    blocked_count = sum([1 for t in all_tasks if task in t.dependencies.all()])
    dependency_score = blocked_count / (len(all_tasks) + 1)  # normalize

    # Combine all factors (weighted sum)
    score = (0.4 * urgency_score +
             0.3 * importance_score +
             0.2 * effort_score +
             0.1 * dependency_score)

    # Include dependencies recursively (add small bonus for each dependency)
    for dep in task.dependencies.all():
        score += 0.05 * calculate_priority(dep, all_tasks, visited)

    return round(score, 4)
