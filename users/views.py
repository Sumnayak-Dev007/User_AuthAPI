from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import status, permissions, generics
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import parsers, renderers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser



class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()



        # Getting the IP from middleware.py
        
        signup_ip = getattr(request, "_client_ip", None)

        response_data = {
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "date_of_birth": user.date_of_birth,
            "signup_ip": signup_ip, 
        }

        return Response(response_data, status=status.HTTP_201_CREATED)




# Custom JWT serializer for login.
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        return token



class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            # If login successful → update IP
            if response.status_code == 200:
                username = request.data.get("username")
                email = request.data.get("email")
                
                user = None
                
                if username:
                    user = CustomUser.objects.filter(username=username).first()
                if not user and email:
                    user = CustomUser.objects.filter(email=email).first()

                client_ip = (
                    request.META.get("HTTP_X_FORWARDED_FOR")
                    or request.META.get("REMOTE_ADDR")
                    or getattr(request, "_client_ip", None)
                )

                if user and client_ip:
                    user.last_login_ip = client_ip
                    user.save(update_fields=["last_login_ip"])

            return response

        except AuthenticationFailed:
            # This is the correct exception for wrong password OR wrong username
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )


# Allows authenticated users to retrieve their own profile information.
# Requires access token in the Authorization header.
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

