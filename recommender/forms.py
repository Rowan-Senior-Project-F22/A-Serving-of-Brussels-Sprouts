from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class ThreadForm(forms.Form):
    username = forms.CharField(label='', max_length=100)


class MessageForm(forms.Form):
    message = forms.CharField(label='', max_length=1000, widget=forms.TextInput(attrs={'size': '100', 'class': 'form-control', 'placeholder': 'Enter message'}))


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

class CustomUserProfileForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-5'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control mb-5'}))
    profile_picture = forms.ImageField(widget=forms.FileInput(attrs={'class': 'mb-5 d-flex'}))
    password1 = forms.CharField(label=_("Password"), required=False, widget=forms.PasswordInput(attrs={'class': "form-control"}))
    password2 = forms.CharField(label=_("Password confirmation"), required=False, widget=forms.PasswordInput(attrs={'class': "form-control"}))
    class Meta:
        model = User
        fields = ("username", "email", "profile_picture", "password1", "password2")

    def save(self, commit=True):
        user = super(CustomUserProfileForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.profile_picture = self.cleaned_data['profile_picture']
        password = self.cleaned_data['password1']
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class LandingAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = ""
        self.fields['username'].widget = forms.widgets.TextInput(attrs={
                'class': 'form-group col-md-12 form-control input-lg',
                'placeholder': 'email',
                'size': '100'
            })
        self.fields['password'].label = ""
        self.fields['password'].widget = forms.widgets.PasswordInput(attrs={
                'class': 'form-group col-md-12 form-control input-lg',
                'placeholder': 'password'
            })


class UserSearchForm(forms.Form):
    search_query = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs={'size': '50', 'class': 'form-control', 'placeholder': 'Search users...'}))


class UserPreferencesForm(forms.Form):

    def __init__(self, genre_seed_options, *args, **kwargs):
        """Initialize a new UserPreferencesForm instance. Provide
		the list of genre seed options available via the form.

		"""
        super().__init__(*args, **kwargs)
        self.fields['genre_seed'].widget.attrs.update({'class': 'form-control rounded-pill'})
        self.fields['genre_seed'].widget.choices = list((i, i) for i in genre_seed_options)

    genre_seed = forms.ChoiceField(widget=forms.Select(choices=[]))


class UserFriendSettingsForm(forms.Form):
    preference = forms.ChoiceField(choices=[('Similar', 'Similar'), ('Opposite', 'Opposite'),
                                            ('Disparate', 'Disparate'), ('Default', 'Default')],
                                   initial="Default",
                                   widget=forms.Select(attrs={'class': "form-control rounded-0"}),
                                   label="Friend Recommendation Preference")


class UserAccountSettingsForm(UserChangeForm):
    """Represents a form that would allow a user to modify
	their existing account settings from within the Account
	Settings page.

	"""
    pass

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
