from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from customer.models import Customer
from customer.serializers import CustomerSerializer, LoginSerializer


class RegisterCustomerView(generics.CreateAPIView):
    """
    API endpoint for customer registration.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a new customer and returns a success message along with the customer ID.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        return Response(
            {"message": "Customer registered successfully", "customer_id": customer.id},
            status=status.HTTP_201_CREATED
        )


class LoginCustomerView(APIView):
    """
    API endpoint for customer login.
    """
    def post(self, request):
        """
        Authenticates the customer and returns an authentication token.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomerDetailView(APIView):
    """
    API endpoint to retrieve authenticated customer details.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns the details of the authenticated customer.
        """
        customer = Customer.objects.get(email=request.user.email)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
