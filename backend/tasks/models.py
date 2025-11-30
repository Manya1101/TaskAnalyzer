from django.db import models
from django.utils import timezone

class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    estimated_hours = models.PositiveIntegerField()
    importance = models.PositiveSmallIntegerField()  # 1-10 scale
    dependencies = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependent_on')
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

