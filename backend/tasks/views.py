from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from .models import Task
from .scoring import compute_score, detect_circular_dependencies


class AnalyzeTasksView(APIView):
    """POST /api/tasks/analyze/ - accepts JSON array of tasks and returns them with scores"""
    def post(self, request):
        payload = request.data

        if not isinstance(payload, list):
            return Response(
                {"error": "Expected a JSON array of tasks"},
                status=status.HTTP_400_BAD_REQUEST
            )

        validated = []
        tasks_index = {}

        # Validate and normalize tasks
        for i, item in enumerate(payload):
            serializer = TaskSerializer(data=item)

            if not serializer.is_valid():
                return Response(
                    {"error": f"Invalid task at index {i}", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = serializer.validated_data
            deps = data.get("dependencies") or []
            dep_ids = [d.id for d in deps]

            t = {
                "id": item.get("id") or (i + 1),
                "title": data.get("title"),
                "due_date": data.get("due_date"),
                "estimated_hours": data.get("estimated_hours"),
                "importance": data.get("importance"),
                "dependencies": dep_ids,
            }

            validated.append(t)
            tasks_index[t["id"]] = t

        # Detect circular dependencies
        cycles = detect_circular_dependencies(
            {tid: t["dependencies"] for tid, t in tasks_index.items()}
        )
        if cycles:
            return Response(
                {"error": "circular_dependencies", "cycles": cycles},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Score tasks
        scored = []
        for t in validated:
            score, explanation = compute_score(t, tasks_index)
            t_copy = t.copy()
            t_copy["score"] = score
            t_copy["explanation"] = explanation
            scored.append(t_copy)

        # Sorting strategies
        strategy = request.query_params.get("strategy", "smart")

        if strategy == "fastest":
            scored.sort(key=lambda x: (x.get("estimated_hours") or 0))

        elif strategy == "impact":
            scored.sort(key=lambda x: -(x.get("importance") or 0))

        elif strategy == "deadline":
            scored.sort(
                key=lambda x: (
                    9999 if x.get("due_date") is None else x.get("due_date")
                )
            )

        else:  # smart balance
            scored.sort(key=lambda x: -x["score"])

        return Response(scored)


class SuggestTasksView(APIView):
    """GET /api/tasks/suggest/ - returns top 3 tasks stored in DB"""
    def get(self, request):
        tasks = Task.objects.all()
        tasks_index = {}

        for t in tasks:
            tasks_index[t.id] = {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date,
                "estimated_hours": t.estimated_hours,
                "importance": t.importance,
                "dependencies": [d.id for d in t.dependencies.all()],
            }

        # Detect cycles
        cycles = detect_circular_dependencies(
            {tid: data["dependencies"] for tid, data in tasks_index.items()}
        )
        if cycles:
            return Response(
                {"error": "circular_dependencies_in_db", "cycles": cycles},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Score tasks
        scored = []
        for t in tasks_index.values():
            score, explanation = compute_score(t, tasks_index)
            t["score"] = score
            t["explanation"] = explanation
            scored.append(t)

        scored.sort(key=lambda x: -x["score"])
        top3 = scored[:3]

        for t in top3:
            t["why"] = f"Score {t['score']}: {t['explanation']}"

        return Response(top3)
