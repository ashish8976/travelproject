from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class User(models.Model):
    fname = models.CharField(max_length=60)
    lname = models.CharField(max_length=60)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=15, default="customer")
    profile_img = models.ImageField(blank=True,null=True, upload_to='profile_img/' )
    
    
    def __str__(self):
        return f"{self.fname}"


class add_tour(models.Model):
    pass


class Destination(models.Model):
    name = models.CharField(max_length=100)  # e.g. "Venice", "Paris"
    country = models.CharField(max_length=100)  # e.g. "Italy", "France"
    image = models.ImageField(upload_to='destinations/')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.country}"


class Tour(models.Model):

    CATEGORY_CHOICES = [
        ('national', 'National'),
        ('international', 'International'),
    ]

    TOUR_TYPE_CHOICES = [
        ('weekend', 'Weekend Tour'),
        ('holiday', 'Holiday Tour'),
        ('family', 'Family Tour'),
        ('beach', 'Beach Tour'),
        ('adventure', 'Adventure Tour'),
        ('honeymoon', 'Honeymoon Tour'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    destination = models.ForeignKey(
        Destination, on_delete=models.SET_NULL, null=True, related_name='tours'
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='national')
    tour_type = models.CharField(max_length=20, choices=TOUR_TYPE_CHOICES)
    description = models.TextField()
    duration_days = models.PositiveIntegerField(help_text="Number of days")
    duration_nights = models.PositiveIntegerField(help_text="Number of nights")
    max_persons = models.PositiveIntegerField(default=10)
    min_persons = models.PositiveIntegerField(default=1)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='tours/')
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        default=5.0,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title
    