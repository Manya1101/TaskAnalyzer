# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from datetime import date

# from .models import Task
# from .serializers import TaskSerializer
# from .utils import calculate_priority

# # ================================
# # List & Create Tasks
# # ================================
# class TaskListCreateView(APIView):
#     """
#     GET: List all tasks with priority scores
#     POST: Create a new task
#     """
#     def get(self, request):
#         tasks = Task.objects.all()
#         data = []

#         for task in tasks:
#             score = calculate_priority(task, tasks)
#             data.append({
#                 "id": task.id,
#                 "title": task.title,
#                 "due_date": task.due_date,
#                 "estimated_hours": task.estimated_hours,
#                 "importance": task.importance,
#                 "dependencies": [d.id for d in task.dependencies.all()],
#                 "completed": task.completed,
#                 "priority_score": score
#             })

#         data = sorted(data, key=lambda x: x["priority_score"], reverse=True)
#         return Response(data)

#     def post(self, request):
#         serializer = TaskSerializer(data=request.data)
#         if serializer.is_valid():
#             task = serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # ================================
# # Analyze Tasks
# # ================================
# class TaskAnalyzeView(APIView):
#     """
#     POST /api/tasks/analyze/
#     Body expected: { "tasks": [ {...} ], "mode": "<mode>" }
#     Supported modes: "Smart Balance" (default), "Fastest Wins", "High Impact", "Deadline Driven"
#     """
#     def post(self, request):
#         tasks_data = request.data.get("tasks", [])
#         mode = request.data.get("mode", "Smart Balance")

#         if not tasks_data:
#             return Response({"error": "No tasks provided"}, status=400)

#         result = []
#         for task in tasks_data:
#             importance = float(task.get("importance", 1))
#             try:
#                 hours = float(task.get("estimated_hours", 1))
#             except:
#                 hours = 1.0

#             try:
#                 due = date.fromisoformat(task.get("due_date"))
#                 days_left = (due - date.today()).days
#                 urgency = 1.0 if days_left < 0 else 1.0 / (days_left + 1)
#             except Exception:
#                 urgency = 0.0

#             # Scoring strategies
#             if mode == "Fastest Wins":
#                 score = round(1.0 / (hours + 0.0001), 4)
#             elif mode == "High Impact":
#                 score = round(importance * 1.0, 4)
#             elif mode == "Deadline Driven":
#                 score = round(urgency * 10.0, 4)
#             else:  # Smart Balance default
#                 score = round(
#                     (importance / 10.0) * 0.6 +
#                     urgency * 0.3 +
#                     (1.0 / (hours + 1.0)) * 0.1,
#                     4
#                 )

#             task_with_score = dict(task)
#             task_with_score["score"] = score
#             result.append(task_with_score)

#         result.sort(key=lambda x: x["score"], reverse=True)
#         return Response({"tasks": result}, status=200)


# # ================================
# # Suggest Top 3 Tasks
# # ================================
# class TaskSuggestView(APIView):
#     """
#     GET /api/tasks/suggest/
#     Returns top 3 tasks to work on today with explanations
#     """
#     def get(self, request):
#         tasks = Task.objects.filter(completed=False)
#         all_tasks = Task.objects.all()

#         task_list = []
#         for task in tasks:
#             score = calculate_priority(task, all_tasks)
#             serializer = TaskSerializer(task)
#             data = serializer.data

#             days_left = (task.due_date - date.today()).days
#             urgency_text = f"Due in {days_left} days" if days_left >= 0 else "Past due!"
#             dependency_count = sum([1 for t in all_tasks if task in t.dependencies.all()])

#             data['score'] = score
#             data['explanation'] = f"{urgency_text}, importance {task.importance}, estimated hours {task.estimated_hours}, blocks {dependency_count} task(s)"
#             task_list.append(data)

#         task_list.sort(key=lambda x: x['score'], reverse=True)
#         return Response(task_list[:3], status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date

from .models import Task
from .serializers import TaskSerializer
from .utils import calculate_priority

# ================================
# List & Create Tasks
# ================================
class TaskListCreateView(APIView):
    """
    GET: List all tasks with priority scores
    POST: Create a new task
    """
    def get(self, request):
        tasks = Task.objects.all()
        data = []

        for task in tasks:
            score = calculate_priority(task, tasks)
            data.append({
                "id": task.id,
                "title": task.title,
                "due_date": str(task.due_date) if task.due_date else None,
                "estimated_hours": float(task.estimated_hours),
                "importance": int(task.importance),
                "dependencies": [d.id for d in task.dependencies.all()],
                "completed": task.completed,
                "score": score  # renamed for frontend consistency
            })

        data.sort(key=lambda x: x["score"], reverse=True)
        return Response(data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ================================
# Analyze Tasks
# ================================
class TaskAnalyzeView(APIView):
    """
    POST /api/tasks/analyze/
    Body expected: { "tasks": [ {...} ], "mode": "<mode>" }
    Supported modes: "Smart Balance" (default), "Fastest Wins", "High Impact", "Deadline Driven"
    """
    def post(self, request):
        tasks_data = request.data.get("tasks", [])
        mode = request.data.get("mode", "Smart Balance")

        if not tasks_data:
            return Response({"error": "No tasks provided"}, status=400)

        result = []
        for task in tasks_data:
            importance = float(task.get("importance", 1))
            try:
                hours = float(task.get("estimated_hours", 1))
            except:
                hours = 1.0

            try:
                due_date = task.get("due_date")
                if due_date:
                    due = date.fromisoformat(due_date)
                    days_left = (due - date.today()).days
                    urgency = 1.0 if days_left < 0 else 1.0 / (days_left + 1)
                else:
                    urgency = 0.0
            except Exception:
                urgency = 0.0

            # Scoring strategies
            if mode == "Fastest Wins":
                score = round(1.0 / (hours + 0.0001), 4)
            elif mode == "High Impact":
                score = round(importance * 1.0, 4)
            elif mode == "Deadline Driven":
                score = round(urgency * 10.0, 4)
            else:  # Smart Balance default
                score = round(
                    (importance / 10.0) * 0.6 +
                    urgency * 0.3 +
                    (1.0 / (hours + 1.0)) * 0.1,
                    4
                )

            task_with_score = dict(task)
            task_with_score["score"] = score
            # Ensure dependencies is always a list
            if not isinstance(task_with_score.get("dependencies", []), list):
                task_with_score["dependencies"] = []
            result.append(task_with_score)

        result.sort(key=lambda x: x["score"], reverse=True)
        return Response({"tasks": result}, status=200)


# ================================
# Suggest Top 3 Tasks
# ================================
class TaskSuggestView(APIView):
    """
    GET /api/tasks/suggest/
    Returns top 3 tasks to work on today with explanations
    """
    def get(self, request):
        tasks = Task.objects.filter(completed=False)
        all_tasks = Task.objects.all()

        task_list = []
        for task in tasks:
            score = calculate_priority(task, all_tasks)
            serializer = TaskSerializer(task)
            data = serializer.data

            days_left = (task.due_date - date.today()).days if task.due_date else 0
            urgency_text = f"Due in {days_left} days" if days_left >= 0 else "Past due!"
            dependency_count = sum([1 for t in all_tasks if task in t.dependencies.all()])

            data['score'] = score
            data['explanation'] = f"{urgency_text}, importance {task.importance}, estimated hours {task.estimated_hours}, blocks {dependency_count} task(s)"
            task_list.append(data)

        task_list.sort(key=lambda x: x['score'], reverse=True)
        return Response(task_list[:3], status=status.HTTP_200_OK)
