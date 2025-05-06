from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True) 
    is_reserved = models.BooleanField(default=False)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=1)  # Total copies available
    copies = models.PositiveIntegerField(default=1)  # Currently available copies
    

    def __str__(self):
        return self.title

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(default=timezone.now)


    class Meta:
        unique_together = ('user', 'book')


    def __str__(self):
        return f"{self.user.username} reserved {self.book.title}"


