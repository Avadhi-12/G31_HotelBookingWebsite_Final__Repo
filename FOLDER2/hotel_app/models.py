from django.db import models
from django.conf import settings
from django.apps import apps

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2, default=1000.00)  # ✅ Add default
    rating = models.FloatField(default=3.5)  # ✅ Add default
    image = models.ImageField(upload_to='hotel_images/', blank=True, null=True)

    amenities = models.CharField(max_length=255, blank=True)  # Comma-separated: "WiFi,Parking,Pool"
    room_type = models.CharField(max_length=20, choices=[
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Suite', 'Suite'),
    ])
    property_type = models.CharField(max_length=50, blank=True)  # Hotel/Resort/Villa

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE, related_name="rooms")
    room_type = models.CharField(max_length=100)
    capacity = models.IntegerField()  # ✅ make sure this exists
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)  # ✅ make sure this exists

    def __str__(self):
        return f"{self.room_type} - {self.hotel.name}"
    
def get_hotel_model():
    # Call apps.get_model in a function to delay the import
    Hotel = apps.get_model('hotel_app', 'Hotel')
    return Hotel

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review on {self.hotel.name}"