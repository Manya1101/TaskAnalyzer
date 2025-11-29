from django.urls import path
from .views import TaskAnalyzeView, TaskSuggestView, TaskListCreateView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list-create'),   # GET/POST tasks
    path('analyze/', TaskAnalyzeView.as_view(), name='task-analyze'),   # POST IDs to analyze
    path('suggest/', TaskSuggestView.as_view(), name='task-suggest'),   # GET top 3 tasks
]
