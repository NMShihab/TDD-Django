from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""  
    def setUp(self):
        self.client = APIClient()
        
    def test_create_valid_user_success(self):
        """Test creating user with valid payload"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'test@123',
            'name': 'Test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        
    def test_user_exist(self):
        """Test user already exist"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'test@123',
            'name': 'Test'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_too_short(self):
        """Test that password is too short"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'te',
            'name': 'Test'
        }
        
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
        
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': "test@gmail.com",
            'password': "abcderfg"
        }
        create_user(**payload)  # create user
        res = self.client.post(TOKEN_URL, payload) 
        self.assertIn('token', res.data)    # check token has
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Check that request was successful
    
    def test_create_token_invalid_credential(self):
        """Test that token is not generate because of invalid input"""
        create_user(email="test@gmail.com", password="password")
        payload = {
            'email': "test@gmail.com",
            'password': "abcderfg"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_no_user(self):
        """Test that token is not generate while user doesn't exist"""
        payload = {
            'email': "test@gmail.com",
            'password': "abcderfg"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_missing_field(self):
        """Test that email and password missing field doesn't give any token"""
        res = self.client.post(TOKEN_URL, {'email': "test@gmail.com", 'password': ""})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_retrive_fails_without_credential(self):
        """Test that user data can not access profile without token"""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
    
class PrivateUserApiTest(TestCase):
    """Test API request those need to be authenticated"""
    def setUp(self):
        self.user = create_user(
            email="test@gmail.com",
            password="test@12345",
            name="Test"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_user_retrive_successfull(self):
        """Successfully retrive User data"""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
    
    def test_post_request_not_allowed(self):
        """Test that post request is not allowed in PROFILE_URL"""
        res = self.client.post(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_profile_data_update_successful(self):
        """Test that user profile can be updated"""
        payload = {'name': "New Test", 'password': "newpassword"}
        res = self.client.patch(PROFILE_URL, payload)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)