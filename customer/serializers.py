from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token

from customer.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return Customer.create_customer(
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            email=validated_data.get('email'),
            phone_number=validated_data.get('phone_number'),
            address=validated_data.get('address'),
            password=validated_data.get('password')
        )

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            customer = Customer.objects.get(email=data["email"])
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Invalid email.")

        if not check_password(data["password"], customer.password):
            raise serializers.ValidationError("Invalid password.")

        token, created = Token.objects.get_or_create(user=customer)
        return {"token": token.key}