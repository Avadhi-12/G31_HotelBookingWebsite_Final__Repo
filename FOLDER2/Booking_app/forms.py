from django import forms
from booking_app.models import Booking, Room

class BookingForm(forms.ModelForm):
    check_in = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    room = forms.ModelChoiceField(queryset=Room.objects.none(), required=True)
    guests = forms.IntegerField(min_value=1, required=True, widget=forms.NumberInput(attrs={'min': 1}))

    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'room', 'guests']

    def __init__(self, *args, **kwargs):
        hotel_id = kwargs.pop('hotel_id', None)  # Safely get hotel_id
        super().__init__(*args, **kwargs)

        if hotel_id:
            # Dynamically set the queryset based on hotel_id
            self.fields['room'].queryset = Room.objects.filter(hotel_id=hotel_id)
