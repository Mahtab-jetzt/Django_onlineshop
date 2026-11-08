from rest_framework import serializers
from .models import user

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = user
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = user
        fields = [
            'id',
            'username',
            'email',
            'password',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        return user.objects.create_user(**validated_data)


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = user
        fields = [
            'id',
            'username',
            'email',
            'password',
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        return value.strip().lower()

    def validate_username(self, value):
        return value.strip()

    def validate(self, attrs):
        new_user = user(
            username=attrs.get('username'),
            email=attrs.get('email')
        )

        try:
            password_validation.validate_password(
                attrs['password'],
                user=new_user
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError({
                'password': error.messages
            })

        return attrs

    def create(self, validated_data):
        return user.objects.create_user(**validated_data)

    
class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            self.token = RefreshToken(attrs['refresh'])
        except TokenError:
            raise serializers.ValidationError({
                'refresh': 'Invalid or expired refresh token.'
            })

        return attrs

    def save(self, **kwargs):
        self.token.blacklist()


