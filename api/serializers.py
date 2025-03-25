from rest_framework import serializers
from .models import CustomUser, Contact, SpamReport
from django.contrib.auth import authenticate

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'phone_number', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            password=validated_data['password'],
            email=validated_data.get('email')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'phone_number', 'email')

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(phone_number=data.get('phone_number'), password=data.get('password'))
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'name', 'phone_number')

class SpamReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpamReport
        fields = ('id', 'phone_number', 'reported_at')

# Serializer for search results
class SearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField()
    phone_number = serializers.CharField()
    spam_count = serializers.IntegerField()
    email = serializers.EmailField(allow_null=True, required=False)
    is_registered = serializers.BooleanField()
