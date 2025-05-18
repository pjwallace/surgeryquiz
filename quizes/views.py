from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from management.models import Topic, Subtopic, Question, Choice, Explanation
from quizes.models import Progress, StudentAnswer
import json
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
@never_cache
def load_quiz_layout(request, subtopic_id, topic_id):
    print('here')
    # get topic name for title
    topic = get_object_or_404(Topic, id=topic_id)
    topic_name = topic.name

    # get subtopic name for title
    subtopic = get_object_or_404(Subtopic, id=subtopic_id)
    subtopic_name = subtopic.name

    # get all the questions for the subtopic
    questions = Question.objects.filter(subtopic_id=subtopic_id).order_by('display_order', 'id')
    questions_count = questions.count()

    # get the button type and page number
    button_type = request.GET.get('button_type')
    page_number = int(request.GET.get('page', 1))

    # if retaking a quiz, update the progress record and delete the previous quiz answers
    if button_type == 'retake':
        success = delete_student_answers(request, subtopic_id)
        if not success:
            # Prevent loading the quiz with stale or inconsistent data
            return redirect('dashboard') 

    # if resuming a quiz, get the first unanswered question
    if button_type == 'resume':
        page_number = get_first_unanswered_question(subtopic_id, request.user)
        if page_number is None:    
            messages.info(
                request,
                "You've already answered all the questions in this quiz. You can review or retake it from your dashboard."
            )
            return redirect('dashboard')

    # set up pagination with 1 question/page
    paginator = Paginator(questions, 1) 
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Unique key for this quiz/subtopic
    session_key = f'quiz_state_{subtopic_id}'
    #quiz_state = request.session.get(session_key, {})

    #Initialize the quiz state
    if session_key not in request.session:
        # get progress record info regarding questions answered and total correct answers
        # This is used when resuming a quiz
        try:
            progress = Progress.objects.get(learner=request.user, subtopic_id=subtopic_id)
            questions_answered = progress.questions_answered
            total_correct = progress.total_correct
        except Progress.DoesNotExist:
            questions_answered = 0
            total_correct = 0

        review_mode = False
        if button_type == 'review':
            review_mode = True

        # Only initialize once
        request.session[session_key] = {
            'page_number': int(page_number),
            'total_pages': paginator.num_pages,
            'question_count': questions.count(),
            'questions_answered': questions_answered,
            'correct_answers': total_correct,
            'incorrect_answers': questions_answered - total_correct,
            'subtopic_id': subtopic_id,
            'review_mode': review_mode,
        }
    quiz_state = request.session[session_key]
    review_mode = quiz_state.get('review_mode', False)
    
    # retrieve the single question to be displayed and question type
    question = page_obj.object_list[0]
    question_id = question.id
    question_type = question.question_type.name 

    # build the context dictionary used by the template
    context = {
        'topic_id': topic_id,
        'topic_name': topic_name,
        'subtopic_id': subtopic_id,
        'subtopic_name': subtopic_name,
        'question': question,
        'question_type': question_type,
        'questions': questions,
        'question_id': question_id,
        'question_count': questions_count,       
        'page_obj': page_obj,
        'page_number': page_number,
        'paginator': paginator, 
        'review_mode': review_mode,
    }

    # rebuild the progress bar showing the answered status of each quiz question
    previous_answers = build_previous_answers(request, subtopic_id)
    if previous_answers:
        context['previous_answers'] = json.dumps(previous_answers) 

    # Only grade the question if button type is not 'resume'
    if button_type != 'resume':
        # determine if the question to be displayed has been previously answered
        previously_answered = StudentAnswer.objects.filter(
            learner = request.user,
            subtopic_id = subtopic_id,
            question_id = question_id
        ).exists()

        # if previously answered, return the choice ids for each answer choice selected
        if previously_answered:
            student_answers = get_student_answers(request, subtopic_id, question_id)

            # grade the quiz question 
            results_dict = create_results_dictionary(question_id, student_answers)
            context['results_dict'] = json.dumps(results_dict) 
            # needed for answered question formatting 
            context['student_answers'] = json.dumps(student_answers)

            # check if the quiz is complete
            if not review_mode:
                if quiz_state['question_count'] == quiz_state['questions_answered']:
                    context['quiz_completed'] = True
                    context['question_count'] = quiz_state['question_count']
                    context['correct_answers'] = quiz_state['correct_answers']
                    context['quiz_score'] = math.ceil((quiz_state['correct_answers'] / quiz_state['question_count']) * 100)

                else:
                    context['quiz_completed'] = False

            # check if an explanation exists for the question
            explanation_text = load_quiz_question_explanation(question_id)
            context['explanation_text'] = explanation_text
   
    return render(request, "quizes/quiz_layout.html", context)


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
        question_type = question.question_type.name

        student_answers = request.POST.getlist("answer")

        context = build_quiz_context(request, subtopic_id, question_id) 
        previous_answers = build_previous_answers(request, subtopic_id)
        if previous_answers:
            context['previous_answers'] = json.dumps(previous_answers)

        # only validate the answer if it hasn't been previously answered
        if not previously_answered:       
            # must select at least one correct answer
            if not student_answers:                
                messages.error(request, "You didn't select an answer.")
                return render(request, "quizes/quiz_layout.html", context)
            
            # if multiple answer question, must select at least 2 answers              
            if question.question_type.name == 'Multiple Answer' and len(student_answers)< 2:               
                messages.error(request, "You must select at least two answers for this type of question.")
                return render(request, "quizes/quiz_layout.html", context)
        
        # grade the quiz question 
        results_dict = create_results_dictionary(question_id, student_answers)                          
        correct_answer = grade_quiz(results_dict, question_type)
        
        # if the question hasn't been previously answered, update quiz state, create or update
        # progress record, and save the student answers
        if not previously_answered:
            
            quiz_state = update_quiz_state(request, subtopic_id, correct_answer)

            # check if the progress record exists or must be created 
            try:           
                Progress.objects.get(learner=request.user, subtopic_id=subtopic_id)
                update_progress_record(request, subtopic_id, question_id, correct_answer)                
            except Progress.DoesNotExist:
                create_progress_record(request, subtopic_id, question_id, correct_answer)

            # save the student answers in the StudentAnswer model
            save_answers(request, subtopic_id, question_id, student_answers)

            # check if quiz is completed
            if quiz_state['question_count'] == quiz_state['questions_answered']:
                process_completed_quiz(request, subtopic_id, question_id, quiz_state)

        page_number = request.POST.get('page')
        button_type = request.POST.get('button_type')
        topic_id = request.POST.get('topic_id')

        url = reverse('load_quiz_layout', args=[subtopic_id, topic_id])
        return redirect(f'{url}?page={page_number}&button_type={button_type}')

def create_results_dictionary(question_id, student_answers):
    question = get_object_or_404(Question, id=question_id)
    results_dict = {}
    # get all the correct answers from the Choice model in list form. Using sets allows for easy comparisions
    correct_choices = set(Choice.objects.filter(question=question, is_correct=True).values_list('id', flat=True))

    # create a set of student choices
    student_selected_choices = set()

    for answer in student_answers:
        choice_id = int(answer)
                
        choice = get_object_or_404(Choice, id=choice_id)
        results_dict[choice_id] = {
            "is_correct": choice.is_correct,
            "selected_by_student": True
        }
        student_selected_choices.add(choice_id)        

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

    return results_dict

def grade_quiz(results_dict, question_type):
    if question_type in ['True/False', 'Multiple Choice']:
        for result in results_dict.values():
            if result['is_correct'] and result['selected_by_student']:
                return True 
        return False
    
    elif question_type == 'Multiple Answer':
        for result in results_dict.values():
            if (not result['is_correct'] and result['selected_by_student']) or \
               (result['is_correct'] and not result['selected_by_student']):
                return False  
        return True

def get_first_unanswered_question(subtopic_id, learner):
    questions = list(
        Question.objects.filter(subtopic_id=subtopic_id)
        .order_by('display_order', 'id')
    )

    answered_ids = set(
        StudentAnswer.objects.filter(
            learner = learner,
            subtopic_id = subtopic_id
        ).values_list('question_id', flat=True).distinct()
    )

    for idx, question in enumerate(questions):
        if question.id not in answered_ids:
            page_number = idx + 1
            return page_number
        
    return None # all questions answered
            
@login_required(login_url='login')
def create_progress_record(request, subtopic_id, question_id, correct_answer):  
    # Create a Progress record if one does not already exist      
    learner = request.user

    total_correct = 0
    if correct_answer:
        total_correct = 1
    
    try:
        progress = Progress(learner=learner, 
                        subtopic_id=subtopic_id, 
                        questions_answered = 1,
                        total_correct = total_correct,
                        initial_score = 0,
                        latest_score = 0
                    )
        progress.save()
    
    except Exception as e:
        context = build_quiz_context(request, subtopic_id, question_id)
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return render(request, "quizes/quiz_layout.html", context)
               
@login_required(login_url='login')
def update_progress_record(request, subtopic_id, question_id, correct_answer):    
    learner = request.user

    # create a Progress instance
    try:
        progress = Progress.objects.get(learner=learner, subtopic_id=subtopic_id)
        progress.questions_answered += 1 
        if correct_answer:
            progress.total_correct += 1  
        progress.save()
    except Progress.DoesNotExist:
        context = build_quiz_context(request, subtopic_id, question_id)
        messages.error(request, "Progress record does not exist.")
        return render(request, "quizes/quiz_layout.html", context)
    except Exception as e:
        context = build_quiz_context(request, subtopic_id, question_id)
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return render(request, "quizes/quiz_layout.html", context)
        
@login_required(login_url='login')
def save_answers(request, subtopic_id, question_id, student_answers):    
    question = get_object_or_404(Question, id=question_id)
      
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
                    is_correct = selected_choices.is_correct                    
                )

                # add the selected_choices many-to-many field using the set() method
                student_answer_obj.selected_choices.set([selected_choices]) 

    except Exception as e:
        context = build_quiz_context(request, subtopic_id, question_id)
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return render(request, "quizes/quiz_layout.html", context)         
    
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

        
def load_quiz_question_explanation(question_id):
    try:
        explanation = Explanation.objects.get(question_id=question_id)
        explanation_text = explanation.text
        return explanation_text        
        
    except Explanation.DoesNotExist:
        return None
    

@login_required(login_url='login')
def get_previous_questions_answered(request, subtopic_id):
    learner = request.user
    
    student_answers = StudentAnswer.objects.filter(
        learner=learner,
        subtopic_id=subtopic_id,
    )
    
    if not student_answers.exists():
        return []
    else:
        answer_question_ids = [answer.question_id for answer in student_answers] 
        # convert to a set to remove duplicate ids that will exist with multiple answer questions
        answer_question_ids = set(answer_question_ids)

        # reconvert to a list 
        answer_question_ids = list(answer_question_ids)
            
        return answer_question_ids

@login_required(login_url='login')
def process_completed_quiz(request, subtopic_id, question_id, quiz_state):    
    learner = request.user
    
    question_count = quiz_state['question_count']
    correct_answers = quiz_state['correct_answers']
    quiz_score = math.ceil((correct_answers / question_count) * 100)

    context = build_quiz_context(request, subtopic_id, question_id)

    # retrieve the progress record
    try:
        progress = Progress.objects.get(learner=learner, subtopic_id=subtopic_id)
        
    except Progress.DoesNotExist:
        messages.error(request, "Progress record doesn't exist.")
        return render(request, "quizes/quiz_layout.html", context)
        
    # update the initial score if necessary and the latest score
    try:
        if progress.initial_score == 0 or progress.initial_score == None:
            progress.initial_score = quiz_score

        progress.latest_score = quiz_score 
        
        progress.save()

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, "quizes/quiz_layout.html", context)
        
    
@login_required(login_url='login')
def delete_student_answers(request, subtopic_id):
    learner = request.user
    student_answers = StudentAnswer.objects.filter(
            learner = learner,
            subtopic_id = subtopic_id
        )
    
    # make sure the StudentAnswer records exist
    if not student_answers.exists():
        messages.error(request, "StudentAnswer records do not exist.") 
        return False

    else:

        # retrieve the Progress record
        try:
            progress = Progress.objects.get(learner=learner, subtopic_id=subtopic_id)
            
        except Progress.DoesNotExist:
                messages.error(request, "Progress record does not exist.") 
                return False

        try:
            with transaction.atomic():
                student_answers.delete()
                
                # update the Progress record
                progress.questions_answered = 0
                progress.total_correct = 0
                progress.latest_score = 0
                progress.save()
                return True

        except Exception as e:           
            messages.error(request, f"An error occurred: {str(e)}")
            return False

def build_quiz_context(request, subtopic_id, question_id):
    question = get_object_or_404(Question, id=question_id)
    questions = Question.objects.filter(subtopic_id=subtopic_id).order_by('display_order', 'id')
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

def build_previous_answers(request, subtopic_id):
    previous_answers = {}
    answered_question_ids = StudentAnswer.objects.filter(
        learner = request.user,
        subtopic_id = subtopic_id
    ).values_list('question_id', flat=True).distinct()

    if not answered_question_ids:
        return {}
    
    # fetch all the Question objects
    questions = Question.objects.filter(id__in=answered_question_ids).select_related('question_type')
    questions_dict = {}
    for question in questions:
        questions_dict[question.id] = question

    # build the dictionary that contains the correct answer for each question. 
    # This will be used by the Javascript function updateProgressBar to indicate whether each
    # answered question is correct or incorrect
    for question_id in answered_question_ids:
        question = questions_dict.get(question_id)
        question_type = question.question_type.name
        student_answers = get_student_answers(request, subtopic_id, question_id)
        results_dict = create_results_dictionary(question_id, student_answers)
        correct_answer = grade_quiz(results_dict, question_type)
        previous_answers[question_id] = correct_answer

    return previous_answers

def update_quiz_state(request, subtopic_id, correct_answer):
    session_key = f'quiz_state_{subtopic_id}'
    quiz_state = request.session.get(session_key, {})

    if quiz_state:
        quiz_state['questions_answered'] += 1

        if correct_answer:
            quiz_state['correct_answers'] += 1
        else:
            quiz_state['incorrect_answers'] += 1

    request.session[session_key] = quiz_state
    request.session.modified = True

    return quiz_state
    
