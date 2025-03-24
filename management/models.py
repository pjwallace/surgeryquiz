from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.text import slugify

def get_default_question_type():
    try:
        return QuestionType.objects.get(name='Multiple Choice').id
    except QuestionType.DoesNotExist:
        return None

# Create all the quiz topics.
class Topic(models.Model):
    name = models.CharField(max_length=40, unique=True) 
    slug = models.SlugField(max_length=50, unique=True, blank=True) 
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, related_name='created_topics')
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='modified_topics')
    is_visible = models.BooleanField(default=True) # topic should be displayed or not
    display_order = models.IntegerField(default=0, blank=False, null=False)

    # create a slug from topic name for URLs
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Topic, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['display_order', 'id']

# Each quiz topic may have multiple subtopics
class Subtopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopics')
    name = models.CharField(max_length=60) 
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, related_name='created_subtopics')
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='modified_subtopics')
    is_visible = models.BooleanField(default=True) # whether subtopic should be displayed or not
    display_order = models.IntegerField(default=0, blank=False, null=False)

    def __str__(self):
        #return f"{self.topic}/{self.name}"
        return self.name
    
    class Meta:
        ordering = ['display_order', 'id']
        unique_together = ('topic', 'name')

class QuestionType(models.Model):
    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    subtopic = models.ForeignKey(Subtopic, related_name='questions', on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType, related_name='questions', on_delete=models.CASCADE, 
        default=get_default_question_type)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, related_name='created_questions')
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='modified_questions')
    display_order = models.IntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.text
    
class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, related_name='created_choices')
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='modified_choices')

    def __str__(self):
        return self.text
    
class Explanation(models.Model):
    question = models.OneToOneField(Question, related_name='explanation', on_delete=models.CASCADE)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, related_name='created_explanations')
    date_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='modified_explanations')

    def __str__(self):
        return self.text

