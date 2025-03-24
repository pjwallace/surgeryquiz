from django import forms
from django.core.exceptions import ValidationError
from management.models import Topic, Subtopic, Question, QuestionType, Choice, Explanation
from collections import OrderedDict
import re

class AddTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']
        widgets = {
            'name' : forms.TextInput(attrs={
                'class' : 'form-control',
                'id' : 'new-topic',
                'autofocus' : True,
                'placeholder' : 'New Topic',
                
            })
        }
        labels = {
            'name' : ""
        } 
    def clean_name(self):
        name =self.cleaned_data.get('name', '').strip().title()
        if not re.match(r'^[A-za-z0-9]', name):
            raise forms.ValidationError("Topic name must start with a letter or a number only.")
        if Topic.objects.filter(name=name).exists():
            raise forms.ValidationError("A topic with this name already exists. Please choose a different name.")
        return name

class RenameTopicForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        label="Choose a topic to rename",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'rename-topic',
        })
    )

    new_topic_name = forms.CharField(
        max_length=40,
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'new-topic-name',
            'placeholder': 'Enter new topic name'
        })
    )
    class Meta:
        model = Topic
        fields = []
    
    def clean_new_topic_name(self):
        new_topic_name =self.cleaned_data.get('new_topic_name', '').strip().title()
        topic = self.cleaned_data.get('topic', '')
        if not re.match(r'^[A-Za-z0-9]', new_topic_name):
            raise forms.ValidationError("Topic name must start with a letter or a number only.")
        if Topic.objects.filter(name=new_topic_name).exists():
            raise forms.ValidationError("A topic with this name already exists. Please choose a different name.")
        # Check if the new topic name is the same as the current topic name
        #if topic and topic.name == new_topic_name:
        #    raise forms.ValidationError("The new topic name must be different from the current name.")
        return new_topic_name 
              
class DeleteTopicForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        queryset= Topic.objects.all(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'topic-to-delete'
        }),
        label='Select a topic to delete'     
    )

    class Meta:
        model = Topic
        fields = []

class AddSubtopicForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        queryset = Topic.objects.all(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'topic-name-subtopic'
        }),
        label='Select a Topic'
        
    )
    class Meta:
        model = Subtopic
        fields = ['topic', 'name']
        widgets = {
            'name' : forms.Textarea(attrs={
            'class' : 'form-control',
            'id' : 'new-subtopic',
            'rows': 1,
            })
        }
        labels = {
            'name': 'Subtopic Name',
        }
            
class RenameSubtopicForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        # only load topics that have at least one subtopic to rename
        queryset= Topic.objects.filter(subtopics__isnull=False).distinct(),
        label="Select a Topic",
       
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'topic-for-renamed-subtopic',
        })
    )

    subtopic = forms.ModelChoiceField(
        queryset = Subtopic.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'choose-subtopic-to-rename',
        }),
        label='Select a subtopic to rename'     
    )
    new_subtopic_name = forms.CharField(
        max_length=60,
        label="",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'new-subtopic-name',
            'rows': 1,
            'placeholder': 'Enter new subtopic name (up to 60 characters)'
        })
    )
    class Meta:
        model = Subtopic
        fields = []   
    
class DeleteSubtopicForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        # only load topics that have at least one subtopic to delete
        queryset= Topic.objects.filter(subtopics__isnull=False).distinct(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'topic-to-choose'
        }),
        label='Select a Topic'     
    )

    subtopic = forms.ModelChoiceField(
        queryset = Subtopic.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'subtopic-to-choose'
        }),
        label='Select a Subtopic to delete'     
    )

    class Meta:
        model = Subtopic
        fields = []

    def clean_subtopic(self):
        subtopic = self.cleaned_data.get('subtopic')
        if not subtopic:
            raise forms.ValidationError("Please select a subtopic.")
        return subtopic
    
class AddQuestionForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        queryset= Topic.objects.filter(subtopics__isnull=False).distinct(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'topic-for-question'
        }),
        label='Select a Topic'     
    )

    subtopic = forms.ModelChoiceField(
        queryset = Subtopic.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'subtopic-for-question'
        }),
        label='Select a Subtopic'     
    )

    question_type = forms.ModelChoiceField(
        queryset= QuestionType.objects.all(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'question-type'
        }),
        label='Select a Question Type'     
    )

    text = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'new-question',
            'placeholder': 'Enter Question',
            'rows': 2,
        })
    )

    class Meta:
        model = Question
        fields = ['subtopic', 'question_type', 'text']

    def __init__(self, *args, **kwargs):
        super(AddQuestionForm, self).__init__(*args, **kwargs)         
        self.fields['subtopic'].queryset = Subtopic.objects.none()

        # Set initial value for question_type to the default value (Multiple Choice), if it exists.
        try:
            default_question_type = QuestionType.objects.get(name='Multiple Choice')
            self.fields['question_type'].initial = default_question_type
        except QuestionType.DoesNotExist:
            pass  
        
        # Reorder the fields
        self.fields = OrderedDict([
            ('topic', self.fields['topic']),
            ('subtopic', self.fields['subtopic']),
            ('question_type', self.fields['question_type']),
            ('text', self.fields['text']),
        ])

class AddChoiceForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']
        widgets = {
            'text' : forms.Textarea(attrs={
                'class' : 'form-control',
                'rows' : 2,
                'placeholder' : 'Answer Choice',              
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                
            })
        }
        labels = {
            'text' : "",
            'is_correct': "Correct"
        } 

class EditQuestionForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        # only select topics that have subtopics with questions
        queryset= Topic.objects.filter(subtopics__questions__isnull=False).distinct(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'topic-for-edit-question'
        }),
        label='Select a Topic'     
    )

    subtopic = forms.ModelChoiceField(
        queryset = Subtopic.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'subtopic-for-edit-question'
        }),
        label='Select a Subtopic'     
    )

    text = forms.ModelChoiceField(
        queryset = Question.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'question-to-edit'
        }),
        label='Select a Question to edit or delete'
    )

    class Meta:
        model = Question
        fields = ['subtopic', 'text']

    def __init__(self, *args, **kwargs):
        super(EditQuestionForm, self).__init__(*args, **kwargs)

        # Reorder the fields
        self.fields = OrderedDict([
            ('topic', self.fields['topic']),
            ('subtopic', self.fields['subtopic']),
            ('text', self.fields['text']),
            
        ])

class GetAllQuestionsForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        # only select topics that have subtopics with questions
        queryset= Topic.objects.filter(subtopics__questions__isnull=False).distinct(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'topic-for-get-all-questions'
        }),
        label='Select a Topic'     
    )

    subtopic = forms.ModelChoiceField(
        queryset = Subtopic.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'subtopic-for-get-all-questions'
        }),
        label='Select a Subtopic'     
    )

    class Meta:
        model = Question
        fields = ['subtopic']

    def __init__(self, *args, **kwargs):
        super(GetAllQuestionsForm, self).__init__(*args, **kwargs)

        # Reorder the fields
        self.fields = OrderedDict([
            ('topic', self.fields['topic']),
            ('subtopic', self.fields['subtopic']),
                        
        ])

class EditQuestionTextForm(forms.Form):
    topic = forms.CharField(label='Topic', max_length=40, 
            widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'topic-name', 'readonly': 'readonly'}))
    subtopic = forms.CharField(label='Subtopic', max_length=60, 
            widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'subtopic-name', 'readonly': 'readonly'}))
    question_type = forms.CharField(label='Question Type', max_length=25, 
            widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'question-name', 'readonly': 'readonly'}))
    text = forms.CharField(label='Question', 
            widget=forms.Textarea(attrs={'rows':2, 'class': 'form-control', 'id': 'question-text'}))

class AddExplanationForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.filter(
            subtopics__isnull = False, # topic must have a subtopic
            subtopics__questions__isnull = False, # subtopic must have questions
            subtopics__questions__explanation__isnull = True # question can't have an explanation already
        ).distinct(),  
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'topic-for-add-explanation'
        }),
        label='Select a Topic'     
    )

    subtopic = forms.ModelChoiceField(
        queryset = Subtopic.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'subtopic-for-add-explanation'
        }),
        label='Select a Subtopic'     
    )

    question = forms.ModelChoiceField(
        queryset = Question.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'question-for-add-explanation'
        }),
        label='Select a Question'
    )

    text = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'text-for-add-explanation',
            'placeholder': 'Explanation',
            'disabled': 'disabled',
            'rows': 5,
        })
    )

    class Meta:
        model = Explanation
        fields = ['question', 'text']

    def __init__(self, *args, **kwargs):
        super(AddExplanationForm, self).__init__(*args, **kwargs)

        # Reorder the fields
        self.fields = OrderedDict([
            ('topic', self.fields['topic']),
            ('subtopic', self.fields['subtopic']),
            ('question', self.fields['question']),
            ('text', self.fields['text']),
            
        ])

class EditExplanationForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.filter(
            subtopics__isnull = False, # topic must have a subtopic
            subtopics__questions__isnull = False, # subtopic must have questions
            subtopics__questions__explanation__isnull = False # question must have an explanations
        ).distinct(), 
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'topic-for-edit-explanation'
        }),
        label='Select a Topic'     
    )

    subtopic = forms.ModelChoiceField(
        queryset = Subtopic.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'subtopic-for-edit-explanation'
        }),
        label='Select a Subtopic'     
    )

    question = forms.ModelChoiceField(
        queryset = Question.objects.none(),
        widget=forms.Select(attrs={
            'class' : 'form-control',
            'id' : 'question-for-edit-explanation'
        }),
        label='Select a Question'
    )

    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'text-for-edit-explanation',
            'rows': 5,
            'disabled': 'disabled',
        }),
        label='Edit Explanation'
    )

    class Meta:
        model = Explanation
        fields = ['question', 'text']

    def __init__(self, *args, **kwargs):
        super(EditExplanationForm, self).__init__(*args, **kwargs)

        # Reorder the fields
        self.fields = OrderedDict([
            ('topic', self.fields['topic']),
            ('subtopic', self.fields['subtopic']),
            ('question', self.fields['question']),
            ('text', self.fields['text']),
            
        ])
