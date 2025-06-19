from django.db import models
from django.contrib.auth.models import User

# This code defines the Books model, which represents a book in the system.
# Each book has a title, author, published year, a foreign key to the User model (indicating ownership), and an availability status.

class Books(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    published_year = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_available=models.BooleanField(default=False) #this field indicates whether the book is available or not.
    #on_delete=models.CASCADE means that if the user is deleted, all their books will also be deleted.
    # The ForeignKey field creates a many-to-one relationship with the User model.
    def __str__(self):#purpose of this method is to return a string representation of the Books model instance.
        # This method is called when the object is printed or converted to a string.
        return self.title
