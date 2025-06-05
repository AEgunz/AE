from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=150, required=False, help_text='Optional.')

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address_line_1', 'city']
        # You can add widgets or labels here if needed, e.g.:
        # labels = {
        #     'address_line_1': 'Address',
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate first_name and last_name from the User instance if available
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        # Save UserProfile part
        profile = super().save(commit=False)
        
        # Save User part
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', user.first_name)
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        
        if commit:
            user.save()
            profile.save()
        return profile
