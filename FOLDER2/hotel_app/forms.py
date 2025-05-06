from django import forms
from .models import Hotel, Room
from .models import Review

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('Single', 'Single'), ('Double', 'Double'), ('Suite', 'Suite')
            ]),
            'property_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('Hotel', 'Hotel'), ('Resort', 'Resort'), ('Villa', 'Villa')
            ]),
            'amenities': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WiFi, Parking, Pool'}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['hotel','room_type', 'capacity', 'price', 'available']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }