# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import parsers, renderers
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

        refresh = RefreshToken.for_user(user)

        # Get the IP from middleware
        
        signup_ip = getattr(request, "_client_ip", None)

        response_data = {
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "date_of_birth": user.date_of_birth,
            "signup_ip": signup_ip,  # include IP in response
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # custom claims can be added here
        token["username"] = user.username
        return token

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer

    # override post to also update last_login_ip if present
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # If authentication succeeded, update user's last_login_ip
        if response.status_code == 200:
            # get username from request data
            username = request.data.get("username")
            email = request.data.get("email")
            # find user
            user = None
            if username:
                try:
                    user = CustomUser.objects.get(username=username)
                except CustomUser.DoesNotExist:
                    user = None
            if not user and email:
                try:
                    user = CustomUser.objects.get(email=email)
                except CustomUser.DoesNotExist:
                    user = None
            # update IP captured by middleware (request.META['REMOTE_ADDR'] or request._client_ip)
            client_ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR") or getattr(request, "_client_ip", None)
            if user and client_ip:
                user.last_login_ip = client_ip
                user.save(update_fields=["last_login_ip"])
        return response

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

