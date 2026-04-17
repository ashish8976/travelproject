from django import forms
from .models import Tour

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = [
            'title', 'slug', 'destination', 'category', 'tour_type',
            'description', 'duration_days', 'duration_nights',
            'max_persons', 'min_persons', 'price_per_person', 'image', 'rating'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Golden Triangle Heritage Tour'
            }),
            'slug': forms.TextInput(attrs={
                'placeholder': 'auto-generated from title'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe the tour experience...',
                'rows': 4
            }),
            'duration_days': forms.NumberInput(attrs={'min': 1}),
            'duration_nights': forms.NumberInput(attrs={'min': 0}),
            'min_persons': forms.NumberInput(attrs={'min': 1}),
            'max_persons': forms.NumberInput(attrs={'min': 1}),
            'price_per_person': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'rating': forms.HiddenInput(), 
        }

