from django.urls import path
from customer.views import RegisterCustomerView, LoginCustomerView, CustomerDetailView

urlpatterns = [
    path('register/', RegisterCustomerView.as_view(), name='register'),
    path('login/', LoginCustomerView.as_view(), name='login'),
    path('me/', CustomerDetailView.as_view(), name='customer-detail'),
]
