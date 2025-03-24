from django.urls import path
from . import views

urlpatterns = [
     path("", views.dashboard, name="dashboard"),
     path("load_quiz_layout/<int:subtopic_id>/<int:topic_id>", views.load_quiz_layout, name="load_quiz_layout"),
     path("load_quiz_questions_and_answers/<int:subtopic_id>", views.load_quiz_questions_and_answers, 
          name="load_quiz_questions_and_answers"),
     path("process_quiz_question/<int:subtopic_id>", views.process_quiz_question, name="process_quiz_question"),
     path("create_progress_record/<int:subtopic_id>", views.create_progress_record, 
          name="create_progress_record"),
     path("update_progress_record/<int:subtopic_id>", views.update_progress_record, 
          name="update_progress_record"),
     path("load_quiz_question_explanation/<int:question_id>", views.load_quiz_question_explanation, 
          name="load_quiz_question_explanation"),
     path("save_answer/<int:question_id>", views.save_answer, name="save_answer"),
     path("get_student_answer/<int:subtopic_id>/<int:question_id>", views.get_student_answer, 
          name="get_student_answer"),
     path("process_completed_quiz/<int:subtopic_id>", views.process_completed_quiz, 
          name="process_completed_quiz"),
     path("get_previous_student_answers/<int:subtopic_id>", views.get_previous_student_answers,
          name="get_previous_student_answers"),
     path("get_previous_results/<int:subtopic_id>", views.get_previous_results, 
          name="get_previous_results"),
     #path("delete_student_answers/<int:subtopic_id>", views.delete_student_answers, 
     #     name="delete_student_answers"),
]