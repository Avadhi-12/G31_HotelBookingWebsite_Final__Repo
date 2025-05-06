# feedback_app/forms.py
from django import forms
from .models import WebsiteFeedback

class WebsiteFeedbackForm(forms.ModelForm):
    class Meta:
        model = WebsiteFeedback
        fields = ['rating', 'comment']

    # Rating field will be optional
    rating = forms.IntegerField(required=False)  