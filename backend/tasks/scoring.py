from datetime import date


def detect_circular_dependencies(task_dependencies):
    """
    Detect circular dependencies in a dictionary:
    {task_id: [dependency_ids]}
    Returns list of cycles (each cycle is a list).
    """
    visited = set()
    recursion_stack = set()
    cycles = []

    def dfs(task, path):
        if task in recursion_stack:
            cycle_start = path.index(task)
            cycles.append(path[cycle_start:])
            return

        if task in visited:
            return

        visited.add(task)
        recursion_stack.add(task)

        for dep in task_dependencies.get(task, []):
            dfs(dep, path + [dep])

        recursion_stack.remove(task)

    for t in task_dependencies:
        if t not in visited:
            dfs(t, [t])

    return cycles


def compute_score(task, tasks_index):
    """
    Score calculation based on:
    - urgency
    - importance
    - low estimated hours
    - dependency weight
    """
    score = 0
    explanation = []

    # 1. Urgency score
    due_date = task.get("due_date")
    if due_date:
        today = date.today()
        days_left = (due_date - today).days
        urgency = max(0, 10 - days_left)
        score += urgency
        explanation.append(f"Urgency: due in {days_left} days → +{urgency}")

    # 2. Importance score
    importance = task.get("importance", 0)
    score += importance * 2
    explanation.append(f"Importance: {importance} → +{importance * 2}")

    # 3. Estimated hours score (favor smaller tasks)
    hours = task.get("estimated_hours", 1)
    if hours > 0:
        time_score = max(0, 10 - hours)
        score += time_score
        explanation.append(f"Low effort: {hours} hours → +{time_score}")

    # 4. Dependency weight: more dependents = more score
    dependents = 0
    for t in tasks_index.values():
        if task["id"] in t.get("dependencies", []):
            dependents += 1

    dep_score = dependents * 3
    score += dep_score
    explanation.append(f"Dependency impact: {dependents} tasks depend on this → +{dep_score}")

    return score, explanation
