from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True) 
    is_reserved = models.BooleanField(default=False)
    

    def __str__(self):
        return self.title

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reserved {self.book.title}"
