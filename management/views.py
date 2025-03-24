from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction, OperationalError
from django.contrib import messages
import json
import time
import re
from django.http import JsonResponse, HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.core.paginator import Paginator

from .models import Topic, Subtopic, Question, QuestionType, Choice, Explanation
from .forms import AddTopicForm, DeleteTopicForm, AddSubtopicForm, DeleteSubtopicForm, RenameTopicForm
from .forms import RenameSubtopicForm, AddQuestionForm, AddChoiceForm, EditQuestionForm, GetAllQuestionsForm
from .forms import EditQuestionTextForm, AddExplanationForm, EditExplanationForm

from .validation import validate_question_and_choices

MAX_RETRIES = 5
RETRY_DELAY = 1  # Delay in seconds

def management_portal(request): 
    # load topics for sidebar
    topics = Topic.objects.filter(is_visible=True).order_by('display_order')
    
    # returning from dashboard
    if 'show_welcome' not in request.session:
        request.session['show_welcome'] = True

    # Check if welcome message should be displayed
    show_welcome = request.session.pop('show_welcome', False)  # Retrieve and remove the flag

    return render(request, 'management/layout.html', {
        'topics' : topics,
        'show_welcome': show_welcome    
    })

@login_required(login_url='login')
def subtopics_for_topic(request, topic_id):
    '''
    Retrieves subtopics for the chosen topic.
    Also returns the number of questions for the subtopic.
    Used for dynamic loading in the sidebar.
    '''
    topic = get_object_or_404(Topic, id=topic_id)
    subtopics = topic.subtopics.filter(is_visible=True).order_by('display_order')
    if subtopics:
        subtopic_data = []
        for subtopic in subtopics:
            question_count = subtopic.questions.count()
            subtopic_data.append({
                'id': subtopic.id,
                'name': subtopic.name,
                'question_count': question_count
            })

        return JsonResponse({'success' : True, 'subtopics' : subtopic_data})
    else:
        return JsonResponse({"success": False,  
                "messages": [{"message": "Subtopic retrieval failed.", "tags": "danger"}]})

@login_required(login_url='login')  
def add_topic(request):
    if request.method == 'GET':
        add_topic_form = AddTopicForm()
        # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')
        return render(request, 'management/add_topic.html', { 
            'add_topic_form' : add_topic_form,
            'topics' : topics,
        })

    elif request.method == 'POST':
        add_topic_form = AddTopicForm(request.POST)
        if add_topic_form.is_valid():
            topic = add_topic_form.save(commit=False)
            topic.created_by = request.user
            topic.modified_by = request.user
            topic.save()       
            
            return JsonResponse({"success": True, "topic_id" : topic.id, "topic_name": topic.name,
                "messages": [{"message": f"{topic.name} has been successfully added.", "tags": "success"}]})
        
        else:
            return JsonResponse({"success": False,
                "messages": [{"message": add_topic_form.errors['name'][0], "tags": "danger"}]})
        
    return HttpResponseNotAllowed(["GET", "POST"])

@login_required(login_url='login')  
def rename_topic(request):
    if request.method == 'GET':
        rename_topic_form = RenameTopicForm()
         # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')
        return render(request, 'management/rename_topic.html', { 
            'rename_topic_form' : rename_topic_form,
            'topics' : topics,
        })
    
    elif request.method == 'POST':
        rename_topic_form = RenameTopicForm(request.POST)

        if rename_topic_form.is_valid():   
            # create a topic instance using the selected topic from the form
            topic = rename_topic_form.cleaned_data['topic']
            # retrieve the current topic name
            old_topic_name = topic.name
            # retrieve the new topic name from the form       
            new_topic_name = rename_topic_form.cleaned_data['new_topic_name']        
               
            # update topic name, modified_by in the topic record       
            topic.name = new_topic_name
            topic.modified_by = request.user
            topic.save()

            return JsonResponse({"success": True, "renamed_topic": new_topic_name, "topic_id": topic.id,
                "messages": [{"message": f"{old_topic_name} has been renamed to {new_topic_name}.", "tags": "success"}]})
        else:
           return JsonResponse({"success": False,
                "messages": [{"message": rename_topic_form.errors['new_topic_name'][0], "tags": "danger"}]})
        
    return HttpResponseNotAllowed(["GET", "POST"])
 
@login_required(login_url='login')
def delete_topic_form(request):
    if request.method == 'GET':
        delete_topic_form = DeleteTopicForm()
        # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')
        return render(request, 'management/delete_topic_form.html', { 
            'delete_topic_form' : delete_topic_form,
            'topics' : topics,
        })
    
    return HttpResponseNotAllowed(["GET"])

@login_required(login_url='login')
def delete_topic(request, topic_id):    
    if request.method == 'POST':        
        try:
            with transaction.atomic():
                topic = Topic.objects.get(pk=topic_id)
                topic.delete()
                return JsonResponse({"success": True,
                        "messages": [{"message": f"Topic '{topic}' has been successfully deleted.", 
                                      "tags": "success"}]})
        except Topic.DoesNotExist:
            return JsonResponse({"success": False,  
                "messages": [{"message": "Topic does not exist.", "tags": "danger"}]}, status=400)
                                  
    return HttpResponseNotAllowed(["POST"])
    
@login_required(login_url='login')  
def get_topics(request):
    topics = Topic.objects.all().values('id', 'name')
    if topics:
        return JsonResponse({'success': True, 'topics': list(topics)}, safe=False)
    else:
        return JsonResponse({"success": False,  
                "messages": [{"message": "An error occurred while retrieving topics.", "tags": "info"}]}, status=500)
    
@login_required(login_url='login')  
def add_subtopic(request):
    if request.method == 'GET':
        add_subtopic_form = AddSubtopicForm()
         # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')
        return render(request, 'management/add_subtopic.html', { 
            'add_subtopic_form' : add_subtopic_form,
            'topics' : topics,
        })
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        topic_id = int(data.get("topic_id", ""))
        name = data.get("name", "").strip()

        # make sure the topic exists
        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return JsonResponse({"success": False,  
                "messages": [{"message": "Invalid topic.", "tags": "danger"}]}, status=400)
        
        # new subtopic name can't be empty
        if not name:
            return JsonResponse({"success": False,  
                "messages": [{"message": "Subtopic name cannot be empty.", "tags": "danger"}]}, status=400)
        
        # subtopic name can't begin with a special character
        if not re.match(r'^[A-Za-z0-9]', name):
            return JsonResponse({"success": False,  
                "messages": [{"message": "Subtopic name must start with a letter or a number only.", 
                              "tags": "danger"}]}, status=400)
        
        # topic/subtopic combination must be unique
        if Subtopic.objects.filter(topic=topic, name=name).exists():
            return JsonResponse({"success": False,  
                "messages": [{"message": "This topic/subtopic combination already exists. Please choose a different subtopic name.", 
                              "tags": "danger"}]}, status=400)

        try:
            subtopic = Subtopic(topic=topic, name=name, created_by=request.user, modified_by=request.user)
            subtopic.save()
            return JsonResponse({"success": True, "subtopic_id": subtopic.id, "subtopic_name": subtopic.name, "topic_id": topic.id,
                "messages": [{"message": f"{name} is now a subtopic of {topic}.", "tags": "success"}]})

        except IntegrityError:
            return JsonResponse({"success": False,  
                "messages": [{"message": "An error occurred while saving this subtopic. Please try again.", 
                "tags": "danger"}]}, status=500)

    return HttpResponseNotAllowed(["GET", "POST"])
        
@login_required(login_url='login')  
def rename_subtopic(request):
    if request.method == 'GET':
        rename_subtopic_form = RenameSubtopicForm()
         # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')
        return render(request, 'management/rename_subtopic.html', { 
            'rename_subtopic_form' : rename_subtopic_form,
            'topics' : topics,
        })
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        topic_id = int(data.get("topic_id", ""))
        subtopic_id = int(data.get("subtopic_id", ""))
        new_subtopic_name = data.get("new_subtopic_name", "").strip()

        # make sure the topic exists
        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return JsonResponse({"success": False,  
                "messages": [{"message": "Invalid topic.", "tags": "danger"}]}, status=400)
        
        # make sure the subtopic exists
        try:
            subtopic = Subtopic.objects.get(pk=subtopic_id)
        except Subtopic.DoesNotExist:
            return JsonResponse({"success": False,  
                "messages": [{"message": "Invalid subtopic.", "tags": "danger"}]}, status=400)

        # new subtopic name can't be empty
        if not new_subtopic_name:
            return JsonResponse({"success": False,  
                "messages": [{"message": "The new subtopic name cannot be empty.", "tags": "danger"}]}, status=400)    
        
        # subtopic name can't begin with a special character
        if not re.match(r'^[A-Za-z0-9]', new_subtopic_name):
            return JsonResponse({"success": False,  
                "messages": [{"message": "The new subtopic name must start with a letter or a number only.", 
                              "tags": "danger"}]}, status=400)
        
        # new subtopic name can't be the same as the old subtopic name
        old_subtopic_name = subtopic.name
        if old_subtopic_name == new_subtopic_name:
            return JsonResponse({"success": False,  
                "messages": [{"message": "The new subtopic name must be different from the current subtopic name.", 
                              "tags": "danger"}]}, status=400)
        
        # topic/new subtopic name must be unique
        if Subtopic.objects.filter(topic=topic, name=new_subtopic_name).exists():
            return JsonResponse({"success": False,  
                "messages": [{"message": "This topic/subtopic combination already exists. Please choose a different subtopic name.", 
                              "tags": "danger"}]}, status=400)

        # update the subtopic instance
        try:
            subtopic.name = new_subtopic_name
            subtopic.modified_by = request.user
            subtopic.save()
            return JsonResponse({"success": True, "subtopic_id" : subtopic.id, "new_subtopic_name" : new_subtopic_name,
                "messages": [{"message": f"{old_subtopic_name} has been renamed to {new_subtopic_name}.", 
                            "tags": "success"}]})
        except Exception as e:
            return JsonResponse({"success": False, 
                "messages": [{"message": f"An error occurred: {str(e)}", "tags": "danger"}]}, status=500)
                
    return HttpResponseNotAllowed(["GET", "POST"])      
        
@login_required(login_url='login')  
def delete_subtopic_form(request):
    if request.method == 'GET':
        delete_subtopic_form = DeleteSubtopicForm()
         # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')
        return render(request, 'management/delete_subtopic_form.html', { 
            'delete_subtopic_form' : delete_subtopic_form,
            'topics' : topics,
        })
    
@login_required(login_url='login')  
def get_subtopics(request, topic_id):
    #subtopics = Subtopic.objects.filter(topic_id=topic_id).values('id', 'name')
    subtopics = Subtopic.objects.filter(topic_id=topic_id, is_visible=True).order_by('display_order').values('id', 'name')

    subtopics_count = subtopics.count() # used for updating the sidebar up/down caret
    
    if subtopics:
        return JsonResponse({'success': True, 'subtopics': list(subtopics), 'subtopics_count': subtopics_count},  
                safe=False)
    else:
        return JsonResponse({"success": False,  
                "messages": [{"message": "An error occurred while retrieving subtopics.", 
                              "tags": "info"}]}, status=500)
    
@login_required(login_url='login')  
def get_subtopics_with_questions(request, topic_id):
    # Ensure the topic exists
    get_object_or_404(Topic, id=topic_id)

    # only retrieve subtopics that have available questions
    #subtopics = Subtopic.objects.filter(topic_id=topic_id, questions__isnull=False).values('id', 'name').distinct()
    subtopics = Subtopic.objects.filter(
    topic_id=topic_id,
    is_visible=True,
    questions__isnull=False
    ).order_by('display_order').values('id', 'name').distinct()

    subtopics_count = subtopics.count() # used for updating the sidebar up/down caret
    
    if subtopics:
        return JsonResponse({'success': True, 'subtopics': list(subtopics), 'subtopics_count': subtopics_count},  
                safe=False)
    else:
        return JsonResponse({"success": False,  
                "messages": [{"message": "An error occurred while retrieving subtopics.", 
                              "tags": "info"}]}, status=404)

@login_required(login_url='login')  
def get_subtopics_with_questions_without_explanations(request, topic_id):
    # Ensure the topic exists
    get_object_or_404(Topic, id=topic_id)

    # only retrieve subtopics that have available questions without explanations
    subtopics = Subtopic.objects.filter(
        topic_id=topic_id, 
        is_visible = True,
        questions__isnull = False, # subtopic has questions
        questions__explanation__isnull=True # questions don't already have explanations 
    ).order_by('display_order').values('id', 'name').distinct()
       
    if subtopics:
        return JsonResponse({'success': True, 'subtopics': list(subtopics)}, safe=False)
    else:
        return JsonResponse({"success": False,  
                "messages": [{"message": "This subtopic's questions already have explanations.", 
                              "tags": "info"}]}, status=404)
    
@login_required(login_url='login')  
def get_subtopics_with_questions_with_explanations(request, topic_id):
    # Ensure the topic exists
    get_object_or_404(Topic, id=topic_id)

    # only retrieve subtopics that have available questions without explanations
    subtopics = Subtopic.objects.filter(
        topic_id=topic_id,
        is_visible = True, 
        questions__isnull = False, # subtopic has questions
        questions__explanation__isnull=False # questions with explanations 
    ).order_by('display_order').values('id', 'name').distinct()
       
    if subtopics:
        return JsonResponse({'success': True, 'subtopics': list(subtopics)}, safe=False)
    else:
        return JsonResponse({"success": False,  
                "messages": [{"message": "This topic's subtopics don't have questions with explanations.", 
                              "tags": "info"}]}, status=404)
    
@login_required(login_url='login')
def delete_subtopic(request, subtopic_id):
    if request.method == 'DELETE':
        try:
            subtopic = Subtopic.objects.get(pk=subtopic_id)
        except Subtopic.DoesNotExist:
            return JsonResponse({"success": False,  
                "messages": [{"message": "Subtopic does not exist.", "tags": "danger"}]}, status=400)
                  
        try:
            subtopic.delete() 
            return JsonResponse({"success": True,
                "messages": [{"message": f"{subtopic} has been successfully deleted.", "tags": "success"}]})               
                        
        except Exception as e:
            return JsonResponse({"success": False,
                "messages": [{"message": f"An error occurred while deleting this subtopic: {str(e)}", "tags": "danger"}]}, status=400)
                
    else:
        # Handle non-DELETE requests 
        return JsonResponse({"success": False,
                "messages": [{"message": "Invalid request method for deleting a subtopic.", "tags": "danger"}]}, status=400) 
    
@login_required(login_url='login')
def add_question_and_choices(request):
    if request.method == 'GET':
        add_question_form = AddQuestionForm()

        # Initially,  4 choice forms are loaded. More can be loaded dynamically
        add_choice_forms = [AddChoiceForm(prefix=str(i)) for i in range(4)]  
        
        # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')
        
        return render(request, 'management/add_question_and_choices.html', { 
            'add_question_form' : add_question_form,
            'add_choice_forms' : add_choice_forms,
            'topics' : topics,
        })
    elif request.method == 'POST':
        data = json.loads(request.body)
        topic_id = int(data.get("topic_id", ""))
        subtopic_id = int(data.get("subtopic_id", ""))
        question_type_id = int(data.get("question_type", ""))
        question_text = data.get("question_text", "").strip()
        choice_forms = data.get("choices", [])   

        # Make sure the subtopic exists
        try:
            subtopic = Subtopic.objects.get(id=subtopic_id)
        except Subtopic.DoesNotExist:
            return JsonResponse({"success": False, 
                "messages": [{"message": "Invalid subtopic selected.", "tags": "danger"}]}, status=400)
                
        # Make sure the question type exists
        try:
            question_type = QuestionType.objects.get(id=question_type_id)
            question_type_name = question_type.name

        except QuestionType.DoesNotExist:
            return JsonResponse({"success": False, 
                "messages": [{"message": "Invalid question type selected.", "tags": "danger"}]}, status=400)
        
        # question error dictionary
        question_errors = {} 

        # validate the question_text field
        if not question_text:
            question_errors['question_text'] = "Please enter a question."
        elif len(question_text) < 10:
            question_errors['question_text'] = "This question is too short. Please provide more information."
        elif Question.objects.filter(subtopic=subtopic, text=question_text).exists():
            question_errors['question_text'] = "This is a duplicate question."     
                                     
        # validate the choice forms 

        # choice error dictionary
        choice_errors = {}              
                
        # create a list of answer choices
        choice_texts = [choice_form['text'].strip() for choice_form in choice_forms]

        # create a list of answer choices        
        choice_answers = [choice_form['is_correct'] for choice_form in choice_forms]

        # each answer choice must be unique
        # Get the choice text from each choice form
        if len(choice_texts) != len(set(choice_texts)): # sets don't have duplicate members
            choice_errors['choices'] = "Duplicate answer choices are not allowed."  

        # no correct answers chosen
        elif choice_answers.count(True) == 0:
            choice_errors['choices'] = "You didn't choose a correct answer." 

        # True/False and multiple choice questions can have only one correct answer checked
        elif question_type_name == 'True/False' or question_type_name == 'Multiple Choice':
            if choice_answers.count(True) > 1:
                choice_errors['choices'] = f"{question_type_name} questions can only have one correct answer."
                            
        # Multiple answer questions must have at least 2 correct answers
        elif question_type_name == 'Multiple Answer' and choice_answers.count(True) < 2:
            choice_errors['choices'] = f"{question_type_name} questions must have at least two correct answers."
           
        if question_errors or choice_errors:
            return JsonResponse({"success": False, 
                                 "question_errors": question_errors,
                                 "choice_errors": choice_errors}, status=400)
        
        # after form validation save the data                       
        try:
            with transaction.atomic():  # if any save operation fails, the database will be rolled back 
            # save the question
                question = Question(subtopic=subtopic, text=question_text, question_type=question_type,
                                    created_by=request.user, modified_by=request.user)
                question.save()

            # save the answer choices
            for choice_form in choice_forms:
                choice = Choice(question=question, text=choice_form['text'], is_correct=choice_form['is_correct'],
                                created_by=request.user, modified_by=request.user)
                choice.save()
                       
        except IntegrityError:
            return JsonResponse({"success": False,  
                "messages": [{"message": "An error occurred while saving this form. Please try again.", "tags": "danger"}]},
                    status=500)
        
        except Exception as e:
            return JsonResponse({"success": False, "messages": [{"message": f"An unexpected error occurred: {str(e)}", "tags": "danger"}]},
                    status=500)
               
        # initialize blank choice forms on form reload
        add_choice_forms = [AddChoiceForm(prefix=str(i)) for i in range(4)]
        add_choice_forms_html = [render_to_string('management/add_choice_form_snippet.html', {'add_choice_form': add_choice_form, 'index': i}) 
                                for i, add_choice_form in enumerate(add_choice_forms)]
              
        return JsonResponse({"success": True, "topic_id": topic_id, "subtopic_id": subtopic_id,
                "question_type_id": question_type_id, "question_type_name": question_type_name, "add_choice_forms": add_choice_forms_html,
                "messages": [{"message": "Question and answer choices have been successfully added.", "tags": "success"}]})

def add_question_and_choices_dynamically(request):
    '''
        This function is called dynamically from the sidebar menu and
        returns the AddQuestionForm and 4 AddChoiceForms
    '''
    if request.method == 'GET':
        add_question_form = AddQuestionForm()

        # Initially,  4 choice forms are loaded. 
        add_choice_forms = [AddChoiceForm(prefix=str(i)) for i in range(4)] 

        context = {
        'add_question_form': add_question_form,
        'add_choice_forms': add_choice_forms,
        }
        
        add_question_and_choices_form_html = render_to_string('management/add_question_and_choices_snippet.html', context, request=request)
        return JsonResponse({"success": True, 
                             'add_question_and_choices_form_html': add_question_and_choices_form_html})
                        
           
def get_question_type_name(request, pk):
    '''
    takes in the question type id from the dropdown menu and returns the question type name
    '''
    try:
        question_type = QuestionType.objects.get(pk=pk)
        return JsonResponse({"success": True, 'name': question_type.name})
    except QuestionType.DoesNotExist:
        return JsonResponse({"success": False,  
                "messages": [{"message": "Question Type not found.", "tags": "danger"}]}, status=404 )

@login_required(login_url='login')    
def get_question_to_edit(request):
    
    if request.method == 'GET':
        
        edit_question_form = EditQuestionForm()

         # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')

        return render(request, 'management/select_question_to_edit.html', { 
            'edit_question_form' : edit_question_form,
            'topics' : topics,
        })
    
@login_required(login_url='login')    
def get_question_to_edit_dynamically(request):
    if request.method == 'GET':
        edit_question_form = EditQuestionForm()
        context = {'edit_question_form': edit_question_form}
        edit_question_form_html = render_to_string('management/select_question_to_edit_dynamically.html',
            context, request=request)
        
        return JsonResponse({"success": True, 'edit_question_form_html': edit_question_form_html})

    
@login_required(login_url='login')    
def load_question_to_edit(request, question_id):
    '''
        This function takes the selected question as a parameter.
        It will return the question type and question text.
        It will also return the answer choices associated with the question.
    '''
    if request.method == 'GET':
    
        # Make sure the question exists
        try:
            question = Question.objects.get(id=question_id)

            # Load the EditQuestionTextForm with initial values
            initial_data = {
                'topic': question.subtopic.topic.name,
                'subtopic': question.subtopic.name,
                'question_type': question.question_type.name,
                'text': question.text
            }

            # Serialize the question
            question_data = {
               "id": question.id,
                "question_type": {
                    "id": question.question_type.id,
                    "name": question.question_type.name
                },
                "text": question.text
            }
                        
        except Question.DoesNotExist:
            return JsonResponse({"success": False, 
                "messages": [{"message": "Invalid question selected.", "tags": "danger"}]}, status=400)
        
        # get the answer choices for the selected question
        # serialize the answer choices
        choices = Choice.objects.filter(question=question)
        choices_data = [{"id": choice.id, "text": choice.text, "is_correct": choice.is_correct} for choice in choices]

        # load the EditQuestionTextForm
        edit_question_text_form = EditQuestionTextForm(initial=initial_data)

        #load the answer choice forms
        edit_choice_forms = [AddChoiceForm(prefix=str(i), instance=choices[i]) for i in range(len(choices_data))] 

        context = {
        'edit_question_text_form': edit_question_text_form,
        'edit_choice_forms': edit_choice_forms,
        'question_id': question_id,
        'question_type': question.question_type.name
        }
        
        edit_question_and_choices_form_html = render_to_string('management/edit_question_and_choices.html', 
                    context, request=request)
        
        
        return JsonResponse({"success": True, 'question': question_data, 'choices': choices_data, 
                             'edit_question_and_choices_form_html': edit_question_and_choices_form_html})

@login_required(login_url='login')
def load_questions(request, subtopic_id):
    '''
    This function takes in a subtopic id and returns all the questions for this subtopic.
    The response object will be returned to the Javascript function loadQuestionsToEdit.
    '''
    if request.method == 'GET':
        questions = Question.objects.filter(
        subtopic_id=subtopic_id).order_by('display_order').values('id', 'text', 'question_type')

        if questions:
            return JsonResponse({"success": True, "questions": list(questions)}, safe=False)
        else:
            return JsonResponse({"success": False,
                    "messages": [{"message": "An error occurred while retrieving questions.", "tags": "info"}]})
        
@login_required(login_url='login')
def load_questions_without_explanation(request, subtopic_id):
    if request.method == 'GET':
        # only select questions without an explanation
        questions_query = Question.objects.filter(
        subtopic_id=subtopic_id, 
        explanation__isnull=True).order_by('display_order')
        
        if not questions_query.exists():
            return JsonResponse({"success": False,
                "messages": [{"message": "All questions for the chosen subtopic already have explanations.", 
                            "tags": "info"}]})
        
        questions_without_explanation = questions_query.values('id', 'text')
        
        # convert QuerySet to a list
        return JsonResponse({"success": True, 
            "questions_without_explanation": list(questions_without_explanation)})
    
    # not a GET request
    else:
        return JsonResponse({"success": False,
            "messages": [{"message": "Invalid request method.", "tags": "info"}]})

        
@login_required(login_url='login')
def load_questions_with_explanation(request, subtopic_id):
    if request.method == 'GET':
        # only select questions with an explanation
        questions_with_explanation = (
            Question.objects.filter(subtopic_id=subtopic_id)
            .filter(explanation__isnull=False).order_by('display_order').values('id', 'text')
        )
        
        if not questions_with_explanation.exists():
            return JsonResponse({"success": False,
                "messages": [{"message": "Chosen subtopic does not have any questions with an explanation.", 
                            "tags": "info"}]})
        
        # convert QuerySet to a list
        return JsonResponse({"success": True, "questions_with_explanation": list(questions_with_explanation)})
    
    # not a GET request
    else:
        return JsonResponse({"success": False,
            "messages": [{"message": "Invalid request method.", "tags": "info"}]})       
    
@login_required(login_url='login')
def get_all_questions_to_edit(request):
    if request.method == 'GET':
        get_all_questions_form = GetAllQuestionsForm()
         # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')
        return render(request, 'management/get_all_questions.html', { 
            'get_all_questions_form' : get_all_questions_form,
            'topics' : topics,
        })

def get_topic_name(request, pk):
    '''
    takes in the topic id from the dropdown menu and returns the topic name
    '''
    try:
        topic = Topic.objects.get(pk=pk)
        return JsonResponse({"success": True, 'topic_name': topic.name})
    except Topic.DoesNotExist:
        return JsonResponse({"success": False,  
                "messages": [{"message": "Topic Name not found.", "tags": "danger"}]}, status=404 )
    
def get_subtopic_name(request, pk):
    '''
    takes in the subtopic id from the dropdown menu and returns the subtopic name
    '''
    try:
        subtopic = Subtopic.objects.get(pk=pk)
        return JsonResponse({"success": True, 'subtopic_name': subtopic.name})
    except Topic.DoesNotExist:
        return JsonResponse({"success": False,  
                "messages": [{"message": "Subtopic Name not found.", "tags": "danger"}]}, status=404 )
    
@login_required(login_url='login')
def edit_question_and_choices(request):    
    if request.method == 'POST':
        
        data = json.loads(request.body)
        question_id = int(data.get("question_id", ""))
        question_text = data.get("question_text", "").strip()
        choice_forms = data.get("choices", []) 
        subtopic_id = int(data.get("subtopic_id", ""))
        question_name = data.get("question_name", "")
        question_type_id = data.get("question_type_id", "")
       
        # Make sure the subtopic exists
        try:
            subtopic = Subtopic.objects.get(id=subtopic_id)
        except Subtopic.DoesNotExist:
            return JsonResponse({"success": False, 
                "messages": [{"message": "Invalid subtopic selected.", "tags": "danger"}]}, status=400)
                
        # Make sure the question type exists
        try:
            question_type = QuestionType.objects.get(id=question_type_id)
            question_type_name = question_type.name

        except QuestionType.DoesNotExist:
            return JsonResponse({"success": False, 
                "messages": [{"message": "Invalid question type selected.", "tags": "danger"}]}, status=400)

        # Load the original question and choices from the database
        original_question = Question.objects.get(id=question_id)
        original_choices = list(Choice.objects.filter(question=original_question))
        
        original_choices_text = [] 
        new_choices = [] 
        
        
        # check if additional answer choices have been included
        if len(choice_forms) > len(original_choices):
                
            for original_choice in original_choices:
                original_choices_text.append(original_choice.text)

            for choice_form in choice_forms:
                if choice_form['text'].strip() not in original_choices_text:
                    new_choices.append(choice_form)
           

        # question error dictionary
        question_errors = {} 

        # only validate the question field if it has been changed
        if not original_question or original_question.text.lower() != question_text.lower():

            # validate the question_text field
            if not question_text:
                question_errors['question_text'] = "Please enter a question."
            elif len(question_text) < 10:
                question_errors['question_text'] = "This question is too short. Please provide more information."
            elif Question.objects.filter(subtopic=subtopic, text=question_text).exists():
                question_errors['question_text'] = "This is a duplicate question."  
        
        # validate the choice forms 

        # choice error dictionary
        choice_errors = {} 

        # create a list of answer choices
        choice_texts = [choice_form['text'] for choice_form in choice_forms]

        # create a list of answer choices        
        choice_answers = [choice_form['is_correct'] for choice_form in choice_forms]  

        # each answer choice must be unique
        # Get the choice text from each choice form
        if len(choice_texts) != len(set(choice_texts)): # sets don't have duplicate members
            choice_errors['choices'] = "Duplicate answer choices are not allowed."  

        # no correct answers chosen
        elif choice_answers.count(True) == 0:
            choice_errors['choices'] = "You didn't choose a correct answer." 

        # True/False and multiple choice questions can have only one correct answer checked
        elif question_type_name == 'True/False' or question_type_name == 'Multiple Choice':
            if choice_answers.count(True) > 1:
                choice_errors['choices'] = f"{question_type_name} questions can only have one correct answer."
                            
        # Multiple answer questions must have at least 2 correct answers
        elif question_type_name == 'Multiple Answer' and choice_answers.count(True) < 2:
            choice_errors['choices'] = f"{question_type_name} questions must have at least two correct answers."
           
        if question_errors or choice_errors:
            return JsonResponse({"success": False, 
                                 "question_errors": question_errors,
                                 "choice_errors": choice_errors}, status=400) 
        
        #after validation, update the database tables
                   
        try:
            success_msg = [] 
            
            for retry in range(MAX_RETRIES):
                with transaction.atomic(): # if any save operation fails, database will be rolled back
                    # update the question table
                    # only update if question text has changed
                                    
                    if original_question.text != question_text:
                        original_question.text = question_text
                        original_question.modified_by = request.user
                        original_question.save()
                        success_msg.append({"message": "Question text successfully updated", "tags": "success"})

                    # update answer choices table if any changes
                    modified = 'no'
                    for choice_form in choice_forms:
                        if choice_form['id']:

                            original_choice = Choice.objects.get(id=choice_form['id'])
                            if choice_form['text'] != original_choice.text or choice_form['is_correct'] != original_choice.is_correct:
                                original_choice.text = choice_form['text']
                                original_choice.is_correct = choice_form['is_correct']
                                original_choice.modified_by = request.user
                                original_choice.save()
                                modified = 'yes'      
                    
                    if modified == 'yes':
                        success_msg.append({"message": "Answer choices successfully updated", "tags": "success"})   
                        
                    # add additional answer choices (if any)
                    if new_choices:
                        for new_choice in new_choices:
                            new_choice = Choice(question=original_question, text=new_choice['text'], is_correct=new_choice['is_correct'],
                                    created_by=request.user, modified_by=request.user)
                            new_choice.save()
                        success_msg.append({"message": "New choices successfully added", "tags": "success"})
                break   

        except IntegrityError:
            return JsonResponse({"success": False, 
                "messages": [{"message": "An error occurred while saving this form. Please try again", 
                              "tags": "danger"}]}, status=500)
        except OperationalError as e:
            if 'database is locked' in str(e):
                if retry < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)  # Wait before retrying
                else:
                    return JsonResponse({"success": False,  
                        "messages": [{"message": f"OperationalError: {str(e)}", 
                        "tags": "danger"}]}, status=500)
                    
            else:
                return JsonResponse({"success": False, 
                        "messages": [{"message": f"OperationalError: {str(e)}", 
                        "tags": "danger"}]}, status=500)
        
        return JsonResponse({"success": True, "messages": success_msg})

@login_required(login_url='login')
def edit_all_questions_and_choices(request):
    
    if request.method == 'GET':
        # get topic + subtopic name for information display in the form
        
        topic_id = request.GET.get('topic')
        topic = get_object_or_404(Topic, id=topic_id)
        subtopic_id = request.GET.get('subtopic')
        subtopic = get_object_or_404(Subtopic, id=subtopic_id)

        # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')

        # load all the questions for the topic/subtopic
        questions = Question.objects.filter(subtopic=subtopic).order_by('display_order')

        if not questions:
            messages.info(request, "There are no questions for this Topic/Subtopic combination")
            return redirect("get_all_questions_to_edit")


        paginator = Paginator(questions, 1)  # Display one question per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        page_range = pagination(page_obj, paginator)
        
        # Get the current question
        question = page_obj.object_list[0]    
        
        initial_data = {
            'topic': question.subtopic.topic.name,
            'subtopic': question.subtopic.name,
            'question_type': question.question_type.name,
            'text': question.text,
        }

        edit_question_text_form = EditQuestionTextForm(initial=initial_data)

        choices = Choice.objects.filter(question=question)
        choices_data = [{"id": choice.id, "text": choice.text, "is_correct": choice.is_correct} for choice in choices]

        #load the answer choice forms
        edit_choice_forms = [AddChoiceForm(prefix=str(i), instance=choices[i]) for i in range(len(choices_data))]

        # can't modify the text field for True/False questions
        if question.question_type.name == 'True/False':
           
            edit_choice_forms[0].fields['text'].widget.attrs['value'] = 'True'
            edit_choice_forms[0].fields['text'].widget.attrs['readonly'] = 'readonly'
            edit_choice_forms[0].fields['text'].widget.attrs['class'] = 'form-control readonly-field'
            edit_choice_forms[1].fields['text'].widget.attrs['value'] = 'False'
            edit_choice_forms[1].fields['text'].widget.attrs['readonly'] = 'readonly' 
            edit_choice_forms[1].fields['text'].widget.attrs['class'] = 'form-control readonly-field'                

        context = {
            'edit_question_text_form': edit_question_text_form,
            'edit_choice_forms': edit_choice_forms,
            'topics': topics,
            'topic': topic,
            'topic_id': topic_id,
            'subtopic': subtopic,
            'subtopic_id': subtopic.id,
            'question_type': question.question_type.name,
            'question_type_id': question.question_type.id,
            'page_obj': page_obj,
            'page_range': page_range,
            'page_number': page_number,
        }
       
        return render(request, 'management/edit_all_questions_and_choices.html', context)

    elif request.method == 'POST':
        # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')

        question_id = request.POST.get('question-id')
        question_text = request.POST.get('text').strip()
        subtopic_id = request.POST.get('subtopic-id')        
        subtopic = get_object_or_404(Subtopic, id=subtopic_id)

        question_type = request.POST.get('question-type')
        question_type_id = request.POST.get('question-type-id')
        question = get_object_or_404(Question, id=question_id)

        # load all the questions for the topic/subtopic
        questions = Question.objects.filter(subtopic=subtopic).order_by('display_order')
        
        # set up pagination
        paginator = Paginator(questions, 1)  # Display one question per page       
        page_number = request.POST.get('page')
        page_obj = paginator.get_page(page_number)
        page_range = pagination(page_obj, paginator)
        

        # Initialize the form with POST data and initial data
        initial_data = {
            'topic': question.subtopic.topic.name,
            'subtopic': question.subtopic.name,
            'question_type': question_type,
            'text': question_text,
        }
        edit_question_text_form = EditQuestionTextForm(request.POST, initial=initial_data)

        # load the answer choices into a list for validation and database updating
        choice_forms = []
        
        for key, value in request.POST.items():
            if key.endswith('-text'):
                index = int(key.split('-')[0])
                choice_id = request.POST.get(f'choice-id-{index+1}', None)
                choice_text = value
                is_correct = f'{index}-is_correct' in request.POST
                
                choice_forms.append({
                    'id': choice_id,
                    'text': choice_text,
                    'is_correct': is_correct,
                })

        #load the answer choice forms
        choices = Choice.objects.filter(question=question)
        edit_choice_forms = [AddChoiceForm(prefix=str(i), initial=choice_forms[i]) for i in range(len(choice_forms))]

        # can't modify the text field for True/False questions
        if question_type == 'True/False':
           
            edit_choice_forms[0].fields['text'].widget.attrs['value'] = 'True'
            edit_choice_forms[0].fields['text'].widget.attrs['readonly'] = 'readonly'
            edit_choice_forms[0].fields['text'].widget.attrs['class'] = 'form-control readonly-field'
            edit_choice_forms[1].fields['text'].widget.attrs['value'] = 'False'
            edit_choice_forms[1].fields['text'].widget.attrs['readonly'] = 'readonly'
            edit_choice_forms[1].fields['text'].widget.attrs['class'] = 'form-control readonly-field'
        
        # Load the original question and choices from the database
        original_question = Question.objects.get(id=question_id)
        original_choices = list(Choice.objects.filter(question=original_question))
                
        original_choices_text = [] 
        new_choices = []

        # check if additional answer choices have been included
        if len(choice_forms) > len(original_choices):
                
            for original_choice in original_choices:
                original_choices_text.append(original_choice.text)

            for choice_form in choice_forms:
                if choice_form['text'] not in original_choices_text:
                    new_choices.append(choice_form)
        
        # Call the validation function
        errors = validate_question_and_choices(subtopic_id, question_type_id, question_text, choice_forms, original_question, original_choices) 
        for error in errors:
            messages.add_message(request, messages.ERROR, error['message'])

        context = {
            'edit_question_text_form': edit_question_text_form,
            'edit_choice_forms': edit_choice_forms,
            'topic': question.subtopic.topic.name,
            'topic_id': question.subtopic.topic.id,
            'subtopic': question.subtopic.name,
            'subtopic_id': question.subtopic.id,
            'question_type': question.question_type.name,
            'question_type_id': question.question_type.id,
            'topics': topics,
            'page_obj': page_obj,
            'page_range': page_range,       
            'page_number': page_number,
        }
        
        if errors:
            return render(request, 'management/edit_all_questions_and_choices.html', context)
        
        else:
            success_msgs = [] 
            for retry in range(MAX_RETRIES): 

            # update the data base
                try:
                    with transaction.atomic(): # if any save operation fails, database will be rolled back
                        # update the question table
                        # only update if question text has changed
                                        
                        if original_question.text != question_text:
                            original_question.text = question_text
                            original_question.modified_by = request.user
                            original_question.save()
                            success_msgs.append({"message": "Question text successfully updated", 
                                                 "tags": "success"})

                        # update answer choices table if any changes
                        modified = 'no'
                        for choice_form in choice_forms:
                            
                            if choice_form['id']:
                                
                                original_choice = Choice.objects.get(id=choice_form['id'])
                                if choice_form['text'] != original_choice.text or choice_form['is_correct'] != original_choice.is_correct:
                                    original_choice.text = choice_form['text']
                                    original_choice.is_correct = choice_form['is_correct']
                                    original_choice.modified_by = request.user
                                    original_choice.save()
                                    modified = 'yes'      
                        
                        if modified == 'yes':
                            success_msgs.append({"message": "Answer choices successfully updated", 
                                                 "tags": "success"})   

                        # add additional answer choices (if any)
                        if new_choices:
                            for new_choice in new_choices:
                                new_choice = Choice(question=original_question, text=new_choice['text'], is_correct=new_choice['is_correct'],
                                        created_by=request.user, modified_by=request.user)
                                new_choice.save()
                            success_msgs.append({"message": "New choices successfully added", 
                                                 "tags": "success"})
                    break
                                
                except IntegrityError:
                    messages.error(request, "An error occurred while saving this form. Please try again.")
                except OperationalError as e:
                    if 'database is locked' in str(e):
                        if retry < MAX_RETRIES - 1:
                            time.sleep(RETRY_DELAY)  # Wait before retrying
                        else:
                            messages.error(request, f"OperationalError: {str(e)}")
                    else:
                        messages.error(request, f"OperationalError: {str(e)}") 

        # update with form with new choices
        choices = Choice.objects.filter(question=question)
        # Prepare the forms with the updated choices
        edit_choice_forms = [AddChoiceForm(prefix=str(i), instance=choice) for i, choice in enumerate(choices)]
        context['edit_choice_forms'] = edit_choice_forms
        
        for success_msg in success_msgs:
                    messages.add_message(request, messages.SUCCESS, success_msg['message'])

        return render(request, 'management/edit_all_questions_and_choices.html', context)

@login_required(login_url='login')    
def delete_question(request, question_id): 
    data = json.loads(request.body)
    subtopic_id = int(data.get("subtopic_id", ""))
    subtopic = get_object_or_404(Subtopic, id=subtopic_id)

    if request.method == 'DELETE':
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return JsonResponse({"success": False,  
                "messages": [{"message": "Question does not exist.", "tags": "danger"}]}, status=404)
     
        try:
            question.delete()

            # get question count for updating the sidebar menu
            question_count = subtopic.questions.count()

            return JsonResponse({"success": True, "question_count": question_count,
                "messages": [{"message": "Question and answer choices have been successfully deleted.", "tags": "success"}]})
        
        except Exception as e:
            # Catch any other exceptions and return a generic error response
            return JsonResponse({"success": False,
                "messages": [{"message": f"An error occurred: {str(e)}", "tags": "danger"}]}, status=404)

@login_required(login_url='login')        
def add_explanation(request):
    if request.method == 'GET':
        add_explanation_form = AddExplanationForm()

         # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')

        return render(request, 'management/add_explanation.html', { 
            'add_explanation_form' : add_explanation_form,
            'topics' : topics,
        })
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        question_id = data.get('question_id')
        explanation_text = data.get('explanation_text').strip()
        
        try:
            question = Question.objects.get(pk=question_id)
            if hasattr(question, 'explanation'):
                return JsonResponse({"success": False,
                    "messages": [{"message": "This question already has an explanation.", "tags": "danger"}]}, status=400)
            else:    
                explanation = Explanation(question = question, text = explanation_text, 
                                created_by = request.user, modified_by = request.user)
                explanation.save()

                # update the topic list
                updated_topics = get_topics_for_add_explanation(request)

                return JsonResponse({"success": True, "topics": list(updated_topics),
                    "messages": [{"message": "Explanation has been successfully added.", "tags": "success"}]}, safe=False)

        except Question.DoesNotExist:
            return JsonResponse({"success": False,
                "messages": [{"message": f"Question with id {question_id} does not exist.", "tags": "danger"}]}, status=400)    
       
        except Exception as e:
            return JsonResponse({"success": False,
                "messages": [{"message": f"An error occurred: {str(e)}", "tags": "danger"}]}, status=400)  
              
@login_required(login_url='login')
def get_topics_for_add_explanation(request):
    topics = Topic.objects.filter(
        subtopics__isnull=False,
        subtopics__questions__isnull=False,
        subtopics__questions__explanation__isnull=True
    ).order_by('display_order').values('id', 'name').distinct()

    return topics
 
    
@login_required(login_url='login')
def load_choices(request, question_id):
    if request.method == 'GET':
        # make sure the question is valid
        try:
            question = Question.objects.get(id=question_id)
            
        except:
            return JsonResponse({"success": False, 
                "messages": [{"message": "Invalid question selected.", "tags": "danger"}]}, status=400)
       
        # get the answer choices for the selected question
        try:
            choices = question.choices.all()
            
            #load the answer choice forms
            choice_forms = [AddChoiceForm(prefix=str(i), instance=choices[i]) for i in range(len(choices))]
            
            # convert choice forms to a string
            choice_forms_html = [render_to_string('management/choice_forms.html', {'choice_forms': choice_forms})]
            
            return JsonResponse({"success": True, "choice_forms": choice_forms_html}, safe=False)
        
        except Exception as e:
            return JsonResponse({
                "success": False, 
                "messages": [{"message": f"Error retrieving choices: {str(e)}", "tags": "danger"}]
            }, status=500)               
    
@login_required(login_url='login')     
def edit_explanation(request):
    if request.method == 'GET':
        edit_explanation_form = EditExplanationForm()

         # load topics for sidebar
        topics = Topic.objects.filter(is_visible=True).order_by('display_order')

        return render(request, 'management/edit_explanation.html', { 
            'edit_explanation_form' : edit_explanation_form,
            'topics' : topics,
        })
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        explanation_id = data.get('explanation_id')
        explanation_text = data.get('explanation_text').strip()
        
        try:
            explanation = Explanation.objects.get(pk=explanation_id)
            explanation.text = explanation_text
            explanation.modified_by = request.user
            explanation.save()

        except Exception as e:
            return JsonResponse({"success": False,
                "messages": [{"message": f"An error occurred: {str(e)}", "tags": "danger"}]}, status=400)

        return JsonResponse({"success": True,
            "messages": [{"message": "Explanation has been successfully edited.", "tags": "success"}]})
    
def get_explanation(request, question_id):
    question = Question.objects.get(pk=question_id)
    try:
        explanation = Explanation.objects.get(question=question)
        explanation_text = explanation.text
        explanation_id = explanation.id

    except Explanation.DoesNotExist:
        return JsonResponse({"success": False,
                "messages": [{"message": f"There is no explanation yet for this question.", "tags": "danger"}]}, status=400)

            
    return JsonResponse({"success": True, 
            "explanation_text": explanation_text, "explanation_id": explanation_id})   

def delete_explanation(request, explanation_id):
    if request.method == 'DELETE':
        try:
            explanation = Explanation.objects.get(pk=explanation_id)
        except Explanation.DoesNotExist:
            return JsonResponse({"success": False,  
                "messages": [{"message": "Explanation does not exist.", "tags": "danger"}]}, status=404)
     
        try:
            explanation.delete()
            
            return JsonResponse({"success": True,
                "messages": [{"message": "Explanation has been successfully deleted.", "tags": "success"}]})
        
        except Exception as e:
            # Catch any other exceptions and return a generic error response
            return JsonResponse({"success": False,
                "messages": [{"message": f"An error occurred: {str(e)}", "tags": "danger"}]}, status=400)

            
def pagination(page_obj, paginator):
    
    # get the page range for the bootstrap html (zero-indexed)
    index = page_obj.number - 1
    max_index = len(paginator.page_range) - 1

    # show 3 pages: current page, previous page (when possible), next page (when possible)
    # calculate the start index and end index for the page range
    start_index = index - 1 if index > 0 else 0
    end_index = index + 2 if index < max_index else index + 1

    # adjust the start index and end index if near the end of their ranges
    if end_index - start_index < 3:
        start_index = max(0, end_index - 3)
        end_index = min(start_index + 3, max_index + 1)

    page_range = paginator.page_range[start_index:end_index] 
    return page_range
