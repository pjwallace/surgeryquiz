from django.contrib import admin
from .models import Progress, StudentAnswer

class ProgressAdmin(admin.ModelAdmin):
    list_display = ('learner', 'subtopic', 'questions_answered', 'initial_score', 'latest_score', 
                    'last_attempted')
    readonly_fields = ['last_attempted']

class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('learner', 'subtopic', 'question', 'display_selected_choices', 'is_correct', 
                    'date_answered')
    readonly_fields = ['date_answered']

    # method to display selected choices as a comma-separated list (Multiple Answer questions)
    def display_selected_choices(self, obj):
        return ", ".join([choice.text for choice in obj.selected_choices.all()])

    # Customize the column header
    display_selected_choices.short_description = 'Selected Choices'


# Register your models here.
admin.site.register(Progress, ProgressAdmin)
admin.site.register(StudentAnswer, StudentAnswerAdmin)
