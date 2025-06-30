from django.shortcuts import render, redirect, get_object_or_404

from .models import Books
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import login, get_user_model, logout as django_logout, BACKEND_SESSION_KEY
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from myproject.utils import build_keycloak_logout_url
from .tokens import account_activation_token
from .forms import CustomUserChangeForm, CustomUserCreationForm
from myapp.decorators import role_required



@login_required
def list_books(request):
    books = Books.objects.filter(user=request.user)
    return render(request, 'list_books.html', {'books': books})

@login_required
@role_required('librarian') # Decorator to restrict access to users with the 'librarian' role
def create_book(request):
    if request.method == 'POST':
        try:
            title = request.POST['title']
            author = request.POST['author']
            published_year_str = request.POST['published_year']

            if not all([title, author, published_year_str]):
                messages.error(request, "All fields (title, author, published year) are required.")
                return render(request, 'create_book.html')

            published_year = int(published_year_str)
            is_available = request.POST.get('is_available', 'off') == 'on'

            Books.objects.create(
                title=title.strip(),
                author=author.strip(),
                published_year=published_year,
                is_available=is_available,
                user=request.user
            )
            messages.success(request, "Book created successfully!")
            return redirect('list_books')
        except (KeyError, ValueError) as e:
            if isinstance(e, KeyError):
                messages.error(request, f"A required field is missing in the form submission: {e}")
            elif isinstance(e, ValueError):
                messages.error(request, "Invalid input for 'Published Year'. Please enter a valid number.")
            return render(request, 'create_book.html')

    return render(request, 'create_book.html')

@login_required
@role_required('librarian')
def update_book(request, book_id):
    book = get_object_or_404(Books, id=book_id, user=request.user)
    if request.method == 'POST':
        try:
            book.title = request.POST['title'].strip()
            book.author = request.POST['author'].strip()
            book.published_year = int(request.POST['published_year'])
            book.is_available = request.POST.get('is_available', 'off') == 'on'
            book.save()
            messages.success(request, "Book updated successfully!")
            return redirect('list_books')
        except (KeyError, ValueError) as e:
            if isinstance(e, KeyError):
                messages.error(request, f"A required field is missing: {e}")
            elif isinstance(e, ValueError):
                messages.error(request, "Invalid input for 'Published Year'. Please enter a valid number.")
            return render(request, 'update_book.html', {'book': book})

    return render(request, 'update_book.html', {'book': book})

@login_required
@role_required('librarian')
def delete_book(request, book_id):
    book = get_object_or_404(Books, id=book_id, user=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('list_books')
    return render(request, 'delete_book.html', {'book': book})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = request.get_host()
            mail_subject = 'Activate your Book Collection account.'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = f"http://{current_site}/activate/{uid}/{token}/"

            message_html = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })

            try:
                send_mail(
                    mail_subject,
                    message_html,
                    None,
                    [user.email],
                    html_message=message_html
                )
                messages.success(request, 'Please confirm your email address to complete the registration. An activation link has been sent to your email.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error sending verification email: {e}. Please try registering again or contact support.')
                user.delete()
                return render(request, 'register.html', {'form': form})
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

def home(request):
    return render(request, 'home.html')

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Thank you for your email confirmation! Your account is now active and you are logged in.')
        return redirect('list_books')
    else:
        messages.error(request, 'Activation link is invalid or has expired!')
        return redirect('home')

@login_required
@require_POST
def smart_logout(request):
    auth_backend = request.session.get(BACKEND_SESSION_KEY)
    if auth_backend == 'myapp.backends.MyOIDCAuthenticationBackend':
        # Grab the id_token from the session BEFORE it's cleared.
        id_token = request.session.get('oidc_id_token')

        # Add the requested print statement for debugging
        print(f"🔍 Debug: id_token found in session for logout: {id_token is not None}")

        # Log the user out of the Django session, which clears the session.
        django_logout(request)

        # Build the full logout URL using the saved id_token and redirect.
        logout_url = build_keycloak_logout_url(request, id_token)
        return redirect(logout_url)
    else:
        django_logout(request)
        messages.success(request, "YOU HAVE BEEN LOGGED OUT SUCCESSFULLY!")
        return redirect('home')
