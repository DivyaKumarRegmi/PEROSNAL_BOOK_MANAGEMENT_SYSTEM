from rest_framework import serializers
from .models import Books
from django.contrib.auth.models import User
# This code defines serializers for the Books model and the User model.

class BookSerializer(serializers.ModelSerializer):
    class Meta:#provides configuration options to django classes including serializers and models
        model = Books #explicitly specifies Books model that django should work with
        # The model to be serialized is specified here.
        fields = ['id', 'title', 'author', 'published_year', 'user','is_available']
        # Specify the fields to be included in the serialized output
        # 'id' is included to uniquely identify each book instance
        # 'title', 'author', and 'published_year' are included to provide information about the books.
        # 'user' (the foreign key to the User model) is included to show ownership.
        # The 'id' field is automatically generated by Django for each model instance.
        # This allows the serializer to convert the Books model instances into JSON format
        # and vice versa, making it suitable for use in APIs.
        read_only_fields = ['user']  # User is set by the server, not by client input.
        # This ensures that the 'user' field is read-only in the API,
        # meaning it cannot be modified by the client.
        # The 'user' field is set automatically by the server when a book is created,

        #use of serializer allows for easy conversion between complex data types (like Django models) and JSON,
        # which is commonly used in APIs.

class UserProfileSerializer(serializers.ModelSerializer):
            class Meta:
                model=User
                # The User model is used to represent user profiles in the API.
                fields=['id','username','email', 'first_name', 'last_name','date_joined','last_login','book_count']
                read_only_fields=['id', 'username','date_joined','last_login','book_count'] # book_count is calculated
        # This nested serializer allows the API to include user profile information

            book_count = serializers.SerializerMethodField() # Declare the field

            def get_book_count(self, obj):
                # 'obj' here is the User instance being serialized.
                return Books.objects.filter(user=obj).count()
            # This method calculates the number of books associated with the user.
            # It counts the number of books that belong to the user represented by the serializer instance.
