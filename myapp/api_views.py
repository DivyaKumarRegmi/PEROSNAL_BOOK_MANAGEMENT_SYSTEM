#This code defines the endpoints for managing Books resources, allowing authenticated users to list, create, retrieve, update, and delete their own books.
from .models import Books
from rest_framework import generics, permissions, status
from .serializers import BookSerializer,UserProfileSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer  # Use BookSerializer to serialize the data
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this endpoint

    def get_queryset(self):
        return Books.objects.filter(user=self.request.user)
        # This method retrieves all books that belong to the currently authenticated user.
        # It ensures that users can only access their own books, enhancing security and privacy.

    def perform_create(self,serializer):
        serializer.save(user=self.request.user)
        # This method is called when a new book is created.
        # It saves the book with the currently authenticated user as the owner.
        # The user is automatically set to the currently logged-in user.

class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): #instance method to retrieve the queryset for the view
        return Books.objects.filter(user=self.request.user)
        # This method retrieves a specific book that belongs to the currently authenticated user.
        # It ensures that users can only access, update, or delete their own books.

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class= UserProfileSerializer
    permission_classes=[permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user
        # This method retrieves the user profile of the currently authenticated user.

class LogoutView(APIView):
    """
    API view for user logout. Blacklists the provided refresh token.
    """
    permission_classes = (permissions.IsAuthenticated,) # Only authenticated users can logout

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"detail": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Error blacklisting token.", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)










        