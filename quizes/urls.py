from django.urls import path
from . import views

urlpatterns = [
     path("", views.dashboard, name="dashboard"),
     path("load_quiz_layout/<int:subtopic_id>/<int:topic_id>", views.load_quiz_layout, name="load_quiz_layout"),
     path("process_quiz_question/<int:subtopic_id>/<int:question_id>", views.process_quiz_question, 
          name="process_quiz_question"),
     path("get_student_answers/<int:subtopic_id>/<int:question_id>", views.get_student_answers, 
          name="get_student_answers"),
     #path("process_completed_quiz/<int:subtopic_id>", views.process_completed_quiz, 
     #     name="process_completed_quiz"),
     path("get_previous_questions_answered/<int:subtopic_id>", views.get_previous_questions_answered,
          name="get_previous_questions_answered"),
     #path("get_previous_results/<int:subtopic_id>", views.get_previous_results, 
     #     name="get_previous_results"),
]