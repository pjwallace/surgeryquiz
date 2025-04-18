from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from management.models import Topic, Subtopic, Question, Choice, Explanation
from quizes.models import Progress, StudentAnswer
import json
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time
import math
from django.db import transaction

RETRIES = 3

def dashboard(request):
    # Load topics that have subtopics with questions
    topics = Topic.objects.filter(is_visible=True, subtopics__questions__isnull=False).distinct().order_by('display_order', 'id')
    # retrieve topic subtopics
    for topic in topics:
        topic.filtered_subtopics = topic.subtopics.filter(is_visible =True, questions__isnull=False).distinct().order_by('display_order', 'id')
        # retrieve progress record for each subtopic (if it exists)
        for subtopic in topic.filtered_subtopics:
            subtopic.question_count = subtopic.questions.count()
            subtopic.progress_record = (
                subtopic.progress.filter(learner=request.user)
                .only("questions_answered", "initial_score", "latest_score").first()
            )
    return render(request, 'quizes/dashboard.html', {'topics': topics})
    
@login_required(login_url='login')
def load_quiz_layout(request, subtopic_id, topic_id):
    
    # get topic name for title
    topic = get_object_or_404(Topic, id=topic_id)
    topic_name = topic.name

    # get subtopic name for title
    subtopic = get_object_or_404(Subtopic, id=subtopic_id)
    subtopic_name = subtopic.name

    # get all the questions for the subtopic
    questions = Question.objects.filter(subtopic_id=subtopic_id).order_by('id')
    questions_count = questions.count()

    # get the button type and page number
    button_type = request.GET.get('button_type')
    page_number = request.GET.get('page', 1)

    # set up pagination
    paginator = Paginator(questions, 1) # 1 question/page
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Unique key for this quiz/subtopic
    session_key = f'quiz_state_{subtopic_id}'

    #Initialize the quiz state
    if session_key not in request.session:
        # Only initialize once
        request.session[session_key] = {
            'page_number': int(page_number),
            'total_pages': paginator.num_pages,
            'question_count': questions.count(),
            'questions_answered': 0,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'subtopic_id': subtopic_id,
        }
    quiz_state = request.session[session_key]

    # retrieve the question to be displayed
    question = page_obj.object_list[0]

    context = {
        'topic_id': topic_id,
        'topic_name': topic_name,
        'subtopic_id': subtopic_id,
        'subtopic_name': subtopic_name,
        'question': question,
        'questions': questions,
        'question_id': question.id,
        'question_count': questions_count,        
        'button_type': button_type, 
        'page_obj': page_obj,
        'page_number': page_number,
        'paginator': paginator,  
    }

    return render(request, "quizes/quiz_layout.html", context)

@login_required(login_url='login')
def resume_quiz(request, subtopic_id):
    # get the previously answered questions
    answered_question_ids = get_previous_questions_answered(request, subtopic_id)

    # retrieve the answer choice id for each question
    for question_id in answered_question_ids:
        student_answers = get_student_answers(request, subtopic_id, question_id)
        get_previous_results(question_id, student_answers)

@login_required(login_url='login')
def process_quiz_question(request, subtopic_id, question_id):
    if request.method == 'POST':  
        learner = request.user
        previously_answered = StudentAnswer.objects.filter(
            learner=learner, 
            subtopic_id=subtopic_id, 
            question_id=question_id
        ).exists() 

        question = get_object_or_404(Question, id=question_id)

        student_answers = request.POST.getlist("answer")

        context = build_quiz_context(request, subtopic_id, question_id) 

        # only validate the answer if it hasn't been previously answered
        if not previously_answered:       
            # must select at least one correct answer
            if not student_answers:
                messages.error(request, "You didn't select an answer.")
                return render(request, "quizes/quiz_layout.html", context)
            
            # if multiple answer question, must select at least 2 answers
        
        if not previously_answered:
            if question.question_type.name == 'Multiple Answer' and len(student_answers)< 2:
                messages.error(request, "You must select at least two answers for this type of question.")
                return render(request, "quizes/quiz_layout.html", context)
        
        # grade the quiz question                   
        results_dict = {}
        # get all the correct answers from the Choice model in list form. Using sets allows for easy comparisions
        correct_choices = set(Choice.objects.filter(question=question, is_correct=True).values_list('id', flat=True))

        # create a set of student choices
        student_selected_choices = set()

        for answer in student_answers:
            choice_id = int(answer)
            
            try:
                choice = get_object_or_404(Choice, id=choice_id)
                results_dict[choice_id] = {
                    "is_correct": choice.is_correct,
                    "selected_by_student": True
                }
                student_selected_choices.add(choice_id)
               
            except Choice.DoesNotExist:
                return JsonResponse({"success": False, 
                    "messages": [{"message": "Choice not found.", "tags": "danger"}]}, status=400)

        # For multiple answer questions, there are 2 edge cases to consider:
        # 1) The student didn't choose all the correct answers
        # 2) The student chose all the correct answers but also chose an additional incorrect answer

        # student missed 1 or more correct answers
        missed_correct_answers = correct_choices - student_selected_choices
        # student chose all the correct answers + 1 or more incorrect answers
        extra_incorrect_answers = student_selected_choices - correct_choices

        # add missed correct answers to the results_dict. The student didn't choose all the correct answers
        for choice_id in missed_correct_answers:
            results_dict[choice_id] = {
                "is_correct": True,
                "selected_by_student": False
            }

        # add any extra incorrect answer to results_dict
        for choice_id in extra_incorrect_answers:
            # update existing entry to flag it as an extra incorrect answer
            if choice_id in results_dict:
                results_dict[choice_id]["is_extra_incorrect"] = True
            else:
                # add to results_dict if not already present
                results_dict[choice_id] = {
                    "is_correct": False,
                    "selected_by_student": True,
                    "is_extra_incorrect": True
                }
        
        # check if the progress record exists or must be created
        try:
            progress = Progress.objects.get(learner=request.user, subtopic_id=subtopic_id)
            progress_data = {
                'questions_answered': progress.questions_answered,
                'progress_exists': 'yes'
            }
        except Progress.DoesNotExist:
            progress_data = {
                'progress_exists': 'no'
            }
               
        return JsonResponse({"success": True, "student_answers": student_answers, "results_dict": results_dict, 
                'question_id': question_id, "question_type": question.question_type.name,
                'progress_data': progress_data})    

@login_required(login_url='login') 
@csrf_exempt 
def get_previous_results(request, subtopic_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_answers = data.get("student_answers", [])
        question_id = data.get("question_id", "")

        question = get_object_or_404(Question, id=question_id)

        # grade the quiz question                   
        results_dict = {}

        # get all the correct answers from the Choice model in list form. Using sets allows for easy comparisions
        correct_choices = set(Choice.objects.filter(question=question, is_correct=True).values_list('id', flat=True))

        # create a set of student choices
        student_selected_choices = set()

        for answer in student_answers:
            choice_id = int(answer)
           
            try:
                choice = get_object_or_404(Choice, id=choice_id)
                results_dict[choice_id] = {
                    "is_correct": choice.is_correct,
                    "selected_by_student": True
                }
                student_selected_choices.add(choice_id)
               
            except Choice.DoesNotExist:
                return JsonResponse({"success": False, 
                    "messages": [{"message": "Choice not found.", "tags": "danger"}]}, status=400)
            
        # For multiple answer questions, there are 2 edge cases to consider:
        # 1) The student didn't choose all the correct answers
        # 2) The student chose all the correct answers but also chose an additional incorrect answer

        # student missed 1 or more correct answers
        missed_correct_answers = correct_choices - student_selected_choices
        # student chose all the correct answers + 1 or more incorrect answers
        extra_incorrect_answers = student_selected_choices - correct_choices

        # add missed correct answers to the results_dict. The student didn't choose all the correct answers
        for choice_id in missed_correct_answers:
            results_dict[choice_id] = {
                "is_correct": True,
                "selected_by_student": False
            }

        # add any extra incorrect answer to results_dict
        for choice_id in extra_incorrect_answers:
            # update existing entry to flag it as an extra incorrect answer
            if choice_id in results_dict:
                results_dict[choice_id]["is_extra_incorrect"] = True
            else:
                # add to results_dict if not already present
                results_dict[choice_id] = {
                    "is_correct": False,
                    "selected_by_student": True,
                    "is_extra_incorrect": True
                }

        return JsonResponse({"success": True, "results_dict": results_dict, 
                "question_type": question.question_type.name })

            
@login_required(login_url='login')
def create_progress_record(request, subtopic_id):
    if request.method == 'POST':
        learner = request.user

        for _ in range(RETRIES):

            # if database is locked from a previous operation, retry 3 times
            try:
                progress = Progress(learner=learner, subtopic_id=subtopic_id, questions_answered=1)
                progress.save()

                return JsonResponse({"success": True})
            
            except IntegrityError:
                return JsonResponse({"success": False,  
                    "messages": [{"message": "An error occurred while creating this record.", "tags": "danger"}]},
                        status=500)
            
            except Exception as e:
                if "database is locked" in str(e).lower():
                    time.sleep(0.3) 
                else:
                    return JsonResponse({"success": False, "messages": [{"message": f"An unexpected error occurred: {str(e)}", "tags": "danger"}]},
                        status=500)  
                
        return JsonResponse({
            "success": False,
            "messages": [{"message": "Database is locked after multiple attempts.", "tags": "danger"}]
        }, status=500)           
    
@login_required(login_url='login')
def update_progress_record(request, subtopic_id):
    if request.method == 'PUT':
        learner = request.user

         # create a Progress instance
        try:
            progress = Progress.objects.get(learner=learner, subtopic_id=subtopic_id)
            questions_answered = progress.questions_answered
        except Progress.DoesNotExist:
            return JsonResponse({"success": False, 
                "messages": [{"message": "Progress record does not exist.", "tags": "danger"}]}, status=400)
        
        for _ in range(RETRIES):        
            # update number of questions answered
            try:
                progress.questions_answered = questions_answered + 1           
                progress.save()
                return JsonResponse({"success": True})
        
            except Exception as e:
                if "database is locked" in str(e).lower():
                    time.sleep(0.3) 
                else:
                    return JsonResponse({"success": False, "messages": [{"message": f"An unexpected error occurred: {str(e)}", "tags": "danger"}]},
                        status=500) 
                
        return JsonResponse({
            "success": False,
            "messages": [{"message": "Database is locked after multiple attempts.", "tags": "danger"}]
        }, status=500)          

@login_required(login_url='login')
def save_answer(request, question_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_answers = data.get("student_answers", [])
        question = get_object_or_404(Question, id=question_id)

        # if database is locked from a previous operation, retry 3 times
        for _ in range(RETRIES):
            try:
                # all updates must succeed. Roll back to initial state if any update fails
                with transaction.atomic():
        
                    # iterate over the student_answer list and create a StudentAnswer record for each answer
                    # each answer is a choice id
                    # question type 'Multiple Answer' will have at least 2 answers
                    for student_answer in student_answers:
                        selected_choices = Choice.objects.get(pk=student_answer)

                        # save the student's answers                        
                        student_answer_obj = StudentAnswer.objects.create(
                            learner = request.user,
                            question = question,
                            subtopic = question.subtopic,
                            is_correct=selected_choices.is_correct                    
                        )

                        # add the selected_choices many-to-many field using the set() method
                        student_answer_obj.selected_choices.set([selected_choices]) 
                
                # database operations were successful
                return JsonResponse({"success": True})

            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                if "database is locked" in str(e).lower():
                    # If the database is locked, wait before retrying
                    time.sleep(0.5)  
                else:
                    # For other exceptions, return immediately
                    return JsonResponse({
                        "success": False,
                        "messages": [{"message": error_message, "tags": "danger"}]
                    }, status=500)

        # If retry fails, return an error
        return JsonResponse({
            "success": False,
            "messages": [{"message": "Database error occurred.", "tags": "danger"}]
        }, status=500)       
    
@login_required(login_url='login')
def get_student_answers(request, subtopic_id, question_id):
    learner = request.user

    # Query all selected choice IDs 
    selected_choice_ids = StudentAnswer.objects.filter(
        learner=learner,
        subtopic_id=subtopic_id,
        question_id=question_id
    ).values_list('selected_choices__id', flat=True)

    return list(selected_choice_ids)

        
@login_required(login_url='login')
def load_quiz_question_explanation(request, question_id):
    try:
        explanation = Explanation.objects.get(question_id=question_id)
        context = {
            'explanation_text': explanation.text
        }
       
        quiz_explanation_html = render_to_string('quizes/quiz_explanation.html', context)
        
    except Explanation.DoesNotExist:
        return JsonResponse({"success": False})
    
    except Exception as e:
            return JsonResponse({"success": False, 
                "messages": [{"message": f"An error occurred: {str(e)}", "tags": "danger"}]}, status=500)
    
    return JsonResponse({"success": True, "quiz_explanation_html": quiz_explanation_html})

@login_required(login_url='login')
def get_previous_questions_answered(request, subtopic_id):
    learner = request.user
    
    student_answers = StudentAnswer.objects.filter(
        learner=learner,
        subtopic_id=subtopic_id,
    )
    
    if not student_answers.exists():
        messages.error(request, "StudentAnswer record does not exist for this user.")
        return []
    else:
        answer_question_ids = [answer.question_id for answer in student_answers] 
        # convert to a set to remove duplicate ids that will exist with multiple answer questions
        answer_question_ids = set(answer_question_ids)

        # reconvert to a list 
        answer_question_ids = list(answer_question_ids)
            
        return answer_question_ids

@login_required(login_url='login')
def process_completed_quiz(request, subtopic_id):
    if request.method == 'PUT':
        learner = request.user
        data = json.loads(request.body)
        question_count = int(data.get("question_count", ''))
        correct_answers = int(data.get("correct_answers", ''))
        quiz_score = math.ceil((correct_answers / question_count) * 100)

        # retrieve the progress record
        try:
            progress = Progress.objects.get(learner=learner, subtopic_id=subtopic_id)
            
        except Progress.DoesNotExist:
            return JsonResponse({"success": False, 
                "messages": [{"message": "Progress record does not exist.", "tags": "danger"}]}, status=400)
        
        # update the initial score if necessary and the latest score
        try:
            if progress.initial_score == 0 or progress.initial_score == None:
                progress.initial_score = quiz_score 
                progress.latest_score = quiz_score 
            else:
                progress.latest_score = quiz_score

            progress.save()

        except Exception as e:
            return JsonResponse({"success": False, 
                "messages": [{"message": f"An error occurred: {str(e)}", "tags": "danger"}]}, status=500)
        
        context = {
            "quiz_score": quiz_score,
            "question_count": question_count,
            "correct_answers": correct_answers
        }
        quiz_score_html = render_to_string('quizes/quiz_score.html', context)
        
        return JsonResponse({"success": True, "quiz_score_html": quiz_score_html })
    
@login_required(login_url='login')
def delete_student_answers(request, subtopic_id):
    learner = request.user
    student_answers = StudentAnswer.objects.filter(
            learner = learner,
            subtopic_id = subtopic_id
        )
    
    # make sure the StudentAnswer records exist
    if not student_answers.exists():
        messages.error("StudentAnswer records do not exist.") 

    else:

        # retrieve the Progress record
        try:
            progress = Progress.objects.get(learner=learner, subtopic_id=subtopic_id)
            
        except Progress.DoesNotExist:
                messages.error("Progress record does not exist.") 

        try:
            with transaction.atomic():
                student_answers.delete()
                
                # update the Progress record
                progress.questions_answered = 0
                progress.latest_score = None
                progress.save()

        except Exception as e:           
            messages.error(f"An error occurred: {str(e)}")

def build_quiz_context(request, subtopic_id, question_id):
    question = get_object_or_404(Question, id=question_id)
    questions = Question.objects.filter(subtopic_id=subtopic_id)
    topic = question.subtopic.topic
    button_type = request.GET.get('button_type')
    page_number = request.POST.get('page', 1)
    paginator = Paginator(questions, 1)
    page_obj = paginator.get_page(page_number)

    return {
        'topic_id': topic.id,
        'topic_name': topic.name,
        'subtopic_id': subtopic_id,
        'subtopic_name': question.subtopic.name,
        'question': question,
        'questions': questions,
        'question_id': question.id,
        'question_count': questions.count(),
        'button_type': button_type,
        'page_obj': page_obj,
        'page_number': page_number,
        'paginator': paginator,
    }
