# forms.py

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User, Document, YEAR_CHOICES
import re

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        pattern = r'^[a-z]+\.[a-z]+@uzh\.ch$'
        if not re.match(pattern, email):
            raise forms.ValidationError('Email must be in the form firstname.lastname@uzh.ch')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_verified = False  # Will be set to True after email verification
        if commit:
            user.save()
        return user

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'description', 'year', 'semester', 'subject', 'type', 'language']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 15 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 15MB")
            if not file.name.endswith('.pdf'):
                raise forms.ValidationError("File must be a PDF")
            # Additional file type checking can be added here
            return file
        else:
            raise forms.ValidationError("Couldn't read uploaded file")
