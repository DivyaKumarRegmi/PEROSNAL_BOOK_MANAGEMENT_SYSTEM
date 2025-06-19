from django.shortcuts import render, redirect, get_object_or_404
from .models import Books
from django.contrib.auth.forms import UserChangeForm # UserCreationForm (default) is no longer directly used here
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Import Django's messaging framework
from django.contrib.auth import login, get_user_model # Import the login function and get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token # Import your token generator
from .forms import CustomUserChangeForm, CustomUserCreationForm # Import your custom creation form

@login_required
# The @login_required decorator ensures that only authenticated users can access the views below.
# If a user is not authenticated, they will be redirected to the login page.
def list_books(request): #This function will be called when a user visits the /books/ URL.
    books = Books.objects.filter(user=request.user)
    return render(request, 'list_books.html', {'books': books})
@login_required
def create_book(request): #This function will be called when a user visits the /books/create/ URL.
    if request.method == 'POST':
        try:
            title = request.POST['title']
            author = request.POST['author']
            published_year_str = request.POST['published_year']

            if not all([title, author, published_year_str]): # More concise check
                messages.error(request, "All fields (title, author, published year) are required.")
                return render(request, 'create_book.html') # Re-render with error

            published_year = int(published_year_str) # Can raise ValueError
            is_available=request.POST.get('is_available','off')=='on' #this line checks if the checkbox is ticked or unticked and if checked its on otherwise false
            
            Books.objects.create(title=title.strip(), author=author.strip(), published_year=published_year, is_available=is_available, user=request.user) # Add .strip()
            messages.success(request, "Book created successfully!")
            return redirect('list_books')
        except (KeyError, ValueError) as e:
            # Log the error for your records (e.g., import logging; logging.error(f"Error creating book: {e}"))
            if isinstance(e, KeyError):
                messages.error(request, f"A required field is missing in the form submission: {e}")
            elif isinstance(e, ValueError):
                messages.error(request, "Invalid input for 'Published Year'. Please enter a valid number.")
            return render(request, 'create_book.html') # Ensure re-render on error

    return render(request, 'create_book.html')

@login_required
def update_book(request, book_id): #This function will be called when a user visits the /books/update/<book_id>/ URL.
    book = get_object_or_404(Books, id=book_id,user=request.user)
    # get_object_or_404 retrieves the book object or raises a 404 error if not found.
    # It also checks that the book belongs to the currently logged-in user.
    if request.method == 'POST':
        book.title = request.POST['title']
        book.author = request.POST['author']
        book.published_year = request.POST['published_year']
        book.is_available = request.POST.get('is_available', 'off') == 'on'
        book.save()
        return redirect('list_books')
    return render(request, 'update_book.html', {'book': book})

@login_required
def delete_book(request, book_id): #This function will be called when a user visits the /books/delete/<book_id>/ URL.
    book = get_object_or_404(Books, id=book_id,user=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('list_books')
    return render(request, 'delete_book.html', {'book': book})

def register(request): #This function will be called when a user visits the /register/ URL.
    if request.method=='POST':
        form=CustomUserCreationForm(request.POST) # Use your custom form
        if form.is_valid():
            user = form.save(commit=False) # Don't save to DB immediately
            user.is_active = False # Deactivate account until email confirmation
            user.save() # Now save the user with is_active=False

            # Send confirmation email
            current_site = request.get_host() # Gets '127.0.0.1:8000' or your domain
            mail_subject = 'Activate your Book Collection account.'
            # uid and token are used to build the activation link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = f"http://{current_site}/activate/{uid}/{token}/" # We'll create this URL pattern next
            
            # We'll create this email template in the next step
            message_html = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })
            
            try:
                send_mail(
                    mail_subject,
                    message_html, # This can be plain text or HTML
                    None, # Uses DEFAULT_FROM_EMAIL from settings.py
                    [user.email],
                    html_message=message_html # Ensures it's sent as HTML if template is HTML
                )
                messages.success(request, 'Please confirm your email address to complete the registration. An activation link has been sent to your email.')
                return redirect('login') # Or a dedicated "check your email" page
            except Exception as e:
                messages.error(request, f'Error sending verification email: {e}. Please try registering again or contact support.')
                user.delete() # Optional: Rollback user creation if email fails
                return render(request, 'register.html', {'form': form})
    else:
        form=CustomUserCreationForm() # Use your custom form
    # If the request method is GET, it initializes an empty form.
       
    return render(request,'register.html',{'form':form})
    
def home(request): #This function will be called when a user visits the root URL.
    return render(request, 'home.html')    

@login_required
def profile(request): #This function will be called when a user visits the /profile/ URL.
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!') # Use Django messages
            return redirect('profile') # Redirect after POST to show message
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})

def activate(request,uidb64,token):
    User = get_user_model() # Get the currently active User model
    try:
        uid=force_str(urlsafe_base64_decode(uidb64)) # Decode the uidb64 to get the user ID
        user=User.objects.get(pk=uid) # Get the user object using the decoded ID
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user=None # If the user does not exist, we set user to None.   
    
    # This block must be de-indented to be outside the except block.
    if user is not None and account_activation_token.check_token(user,token):
        user.is_active=True # Activate the user account
        user.save() # Save the changes to the user object
        login(request, user) # Log the user in programmatically
        messages.success(request, 'Thank you for your email confirmation! Your account is now active and you are logged in.') # Update message
        return redirect('list_books') # Redirect to the books list
    else:
        # It's good to give a slightly more generic message if the user is None,
        # as "expired" might not be accurate if the uidb64 was tampered with.
        messages.error(request,'Activation link is invalid or has expired!')
        return redirect('home')