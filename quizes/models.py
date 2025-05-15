from django.conf import settings
from django.db import models
from management.models import Subtopic, Question, Choice

class Progress(models.Model):
    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE, related_name='progress')
    questions_answered = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    initial_score = models.IntegerField(null=True, blank=True)
    latest_score = models.IntegerField(null=True, blank=True)
    last_attempted = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('learner', 'subtopic')

class StudentAnswer(models.Model):
    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_answers')
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    selected_choices = models.ManyToManyField(Choice, blank=True)  # Allows for multiple answer questions
    is_correct = models.BooleanField(default=False)
    date_answered = models.DateTimeField(auto_now_add=True)

