from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class ThreadForm(forms.Form):
    username = forms.CharField(label = '', max_length=100)

class MessageForm(forms.Form):
    message = forms.CharField(label = '', max_length= 1000)
from .models import User

class SearchForm(forms.Form):
    artist = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}))
    from_year = forms.IntegerField(required=False)
    to_year = forms.IntegerField(required=False)

'''A custom user form with an email field
designed for this application.
- Brandon Ngo'''
class CustomUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(CustomUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class ListeningRoomForm(forms.Form):
	room_name = forms.CharField(label='', max_length=25)

	def save(self, commit=True):
		room = super(ListeningRoomForm, self).save(commit=False)
		if commit:
			room.save()
		return room