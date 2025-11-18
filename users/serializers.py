# users/serializers.py
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        label="username"
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        label="password"
        
    )
    password_again = serializers.CharField(
        write_only=True, 
        required=True, 
        label="password_again"
    )
    email = serializers.EmailField(
        required=True,
        label="email"
    )
    phone_number = serializers.CharField(
        required=False,
        label="phone_number"
    )
    date_of_birth = serializers.DateField(
        required=False,
        label="date_of_birth",
        input_formats=['%Y-%m-%d']  # optional: for correct input format in browsable API
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "password_again", "phone_number", "date_of_birth")
        extra_kwargs = {"email": {"required": True}}

    def validate(self, data):
        if data["password"] != data["password_again"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        if len(data["password"]) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters."})

        # No other validation (common password, numeric, similarity) is enforced
        
        return data

    def create(self, validated_data):
        validated_data.pop("password_again", None)
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "phone_number", "date_of_birth", "last_login_ip")
