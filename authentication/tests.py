from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class AuthenticationTestCase(TestCase):
    """Basic tests for authentication app"""
    
    def test_user_creation(self):
        """Test that we can create a user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        
    def test_models_import(self):
        """Test that models can be imported without errors"""
        try:
            from . import models
            self.assertTrue(True)
        except ImportError:
            self.fail("Could not import models")


class AuthenticationAPITestCase(APITestCase):
    """API tests for authentication endpoints"""
    
    def test_api_accessible(self):
        """Test that authentication endpoints are accessible"""
        # This is a basic smoke test
        # Add specific endpoint tests based on your authentication URLs
        self.assertTrue(True)  # Placeholder for actual API tests
