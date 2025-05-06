# booking/models.py
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.conf import settings
from hotel_app.models import Hotel, Room

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    CANCELLATION_STATUS = [
        ('none', 'None'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    ]
    cancellation_status = models.CharField(
        max_length=10, choices=CANCELLATION_STATUS, default='none'
    )

    @property
    def can_modify(self):
        # Allow update/cancel only if check-in is more than 24 hours away
        return self.check_in > timezone.now().date() + timedelta(days=1)

    def __str__(self):
        return f'{self.user.username} - {self.hotel.name} ({self.check_in} to {self.check_out})'

    def request_cancellation(self):
        # Update the status to 'pending' for cancellation
        self.cancellation_status = 'pending'
        self.save()

    def approve_cancellation(self):
        # Approve cancellation, update status to 'Cancelled'
        self.cancellation_status = 'approved'
        self.status = 'Cancelled'
        self.save()

    def decline_cancellation(self):
        # Decline the cancellation request, restore to 'Confirmed'
        self.cancellation_status = 'declined'
        self.save()
