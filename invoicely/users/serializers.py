from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

# Serializer for User Signup
# ensuring the password is hashed before serializing

class UserSignupSerializer(serializers.ModelSerializer):
    # the password will not be included in the serialized output returned by the API.
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'company_name', 'email', 'password', 'logo']

    def create(self, validated_data):
        # This method hashes the password before saving the user
        # ensuring secure password storage.
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

# Serializer for User Login
class UserLoginSerializer(serializers.Serializer):
    # the credential to validate
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # validating the user with the authenticate method
    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid login credentials")
        return user

# Serializer for User Details
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'company_name', 'email', 'logo']