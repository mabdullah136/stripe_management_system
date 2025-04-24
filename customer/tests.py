from django.test import TestCase
from rest_framework.test import APIClient


class CustomerAPITestCase(TestCase):
    """
    Test cases to validate customer registration, login, and retrieval.
    """

    def setUp(self):
        """
        Sets up test client and sample customer data.
        """
        self.client = APIClient()
        self.customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "phone_number": "1234567890",
            "address": "123 Main St",
            "password": "securepassword"
        }
        self.register_url = "/customer/register/"
        self.login_url = "/customer/login/"
        self.me_url = "/customer/me/"

    def test_register_customer(self):
        """
        Tests if a customer can be successfully registered.
        """
        response = self.client.post(self.register_url, self.customer_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("customer_id", response.data)

    def test_login_customer(self):
        """
        Tests if a registered customer can log in and receive a token.
        """
        self.client.post(self.register_url, self.customer_data, format='json')
        login_data = {"email": self.customer_data["email"], "password": self.customer_data["password"]}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_get_customer_details(self):
        """
        Tests if an authenticated customer can retrieve their details.
        """
        self.client.post(self.register_url, self.customer_data, format='json')
        login_data = {"email": self.customer_data["email"], "password": self.customer_data["password"]}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data["token"]

        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.customer_data["email"])
