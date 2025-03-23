from django import forms
from learners.models import User
import re
from django.core.exceptions import ValidationError

PG_LEVEL_CHOICES = [
    ('', 'Select your training level'),
    ('PG1', 'PG-1'),
    ('PG2', 'PG-2'),
    ('PG3', 'PG-3'),
    ('PG4', 'PG-4'),
    ('PG5', 'PG-5'),
    ('PG6', 'PG-6'),
    ('PG7', 'PG-7'),
    ('Fellow', 'Fellow'),
    ('Faculty', 'Faculty'),
]

RESIDENCY_PROGRAM_CHOICES = [
    ('', 'Select your training program'),
    ('UTMB', 'University of Texas Medical Branch'),
    ('Other', 'Other Program'),
]

class ProfileForm(forms.Form):
    first_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Last Name'
        })
    )
    preferred_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Preferred Name'
        })
    )
    current_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'readonly': 'readonly',
        })
    )
    new_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Email Address'
        })
    )
    residency_program = forms.ChoiceField(
        choices=RESIDENCY_PROGRAM_CHOICES, required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    pg_level = forms.ChoiceField(
        choices=PG_LEVEL_CHOICES, required=False,
        label='Postgraduate Level',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    cell_phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter cell phone number (digits only)',
        })
    )

    def clean_first_name(self):
        return self.cleaned_data.get('first_name', '').strip()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name', '').strip()
    
    def clean_preferred_name(self):
        return self.cleaned_data.get('preferred_name', '').strip()
        
    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email', '').strip()

        # Skip validation if the field is blank
        if not new_email:
            return new_email

        # Validate email format
        regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(regex_email, new_email):
            raise ValidationError("Invalid email address format.")
        
        # Check if the email is already in use
        if User.objects.filter(email=new_email).exists():
            raise ValidationError("This email is already in use.")
        return new_email
    
    def clean_cell_phone(self):
        cell_phone = self.cleaned_data['cell_phone'].strip()

        # Check if the phone number is digit only
        if cell_phone and not re.match(r'^\+?1?\d*$', cell_phone):
            raise ValidationError('Enter a valid phone number with digits only, no special characters.')
        
        # must be between 9 and 15 digits long (for non U.S. numbers)
        if cell_phone and (len(cell_phone) < 9 or len(cell_phone) > 15):
            raise ValidationError("Phone number must be between 9 and 15 digits.")
        
        return cell_phone
