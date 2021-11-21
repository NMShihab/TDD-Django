from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTest(TestCase):
    
    def setUp(self):
        """Create a super user and a client user"""       
        self.client = Client()
        self.admin_user = get_user_model().objects.create_super_user(
            email="admin@gmail.com",
            password="test@12345"
        )
        
        self.client.force_login(self.admin_user)
        
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="abc@12345",
            name="Test User"
        )
        
    def test_users_listed(self):
        """Test that users are listed"""     
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
         
    def test_user_change_page(self):
        """Test user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)
        
    def test_create_user_page(self):
        """Test that create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)