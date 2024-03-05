from django.test import TestCase, Client
from django.contrib.auth.models import User

# Create your tests here.
class TestModels(TestCase):
    def test_model_User(self):
        username = 'user'
        pwd = 'pass'
        user = User.objects.create_user(username=username, password=pwd)
        self.assertEquals(str(user), username)
        self.assertTrue(isinstance(user, User))