from rest_framework import serializers
from .models import User, FinancialRecord

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password', 'is_active']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'VIEWER')
        )
        return user

class FinancialRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = '__all__'
        read_only_fields = ['is_deleted']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Financial aggregate amount cannot be negative or zero.")
        return value

    def validate_category(self, value):
        if not value.strip():
            raise serializers.ValidationError("Category parameter cannot be blank space.")
        return value.strip()

class RoleChangeSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
