from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email(self):
        """ Test create a new user with email"""
        email = "test@gmail.com"
        password = "test@12345"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """Test the email address normalized"""
        email = "test@GMAIL.COM"
        user = get_user_model().objects.create_user(
            email=email,
            password="test@123"
        )

        self.assertEqual(user.email, email.lower())
    
    def test_valid_email(self):
        """Test user with no email """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test@123")
    
    def test_create_new_super_user(self):
        """Test create new super user"""
        user = get_user_model().objects.create_super_user(
            email="admin@gmail.com",
            password="test@123"
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        
            
