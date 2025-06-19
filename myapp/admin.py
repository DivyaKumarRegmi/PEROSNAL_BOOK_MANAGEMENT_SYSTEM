from django.contrib import admin
from .models import Books
# Register your models here.
admin.site.register(Books)
# Register the Books model with the Django admin site
# This allows you to manage Books instances through the admin interface