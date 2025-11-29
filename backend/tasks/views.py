from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from .utils import calculate_priority
from datetime import date

# Create/Fetch tasks via API
class TaskListCreateView(APIView):
    """
    POST /api/tasks/ → Create a task
    GET /api/tasks/ → Get all tasks
    """
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskAnalyzeView(APIView):
    """
    POST /api/tasks/analyze/
    Accepts a list of task IDs and returns tasks sorted by priority score
    """
    def post(self, request):
        task_ids = request.data.get('task_ids', [])
        tasks = Task.objects.filter(id__in=task_ids)
        all_tasks = Task.objects.all()

        result = []
        for task in tasks:
            score = calculate_priority(task, all_tasks)
            serializer = TaskSerializer(task)
            data = serializer.data
            data['score'] = score
            result.append(data)

        # Sort descending by score
        result.sort(key=lambda x: x['score'], reverse=True)
        return Response(result, status=status.HTTP_200_OK)


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
            data['score'] = score
            explanation = f"Due in {(task.due_date - date.today()).days} days, importance {task.importance}, estimated hours {task.estimated_hours}"
            data['explanation'] = explanation
            task_list.append(data)

        # Sort by score descending
        task_list.sort(key=lambda x: x['score'], reverse=True)
        return Response(task_list[:3], status=status.HTTP_200_OK)
