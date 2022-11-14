from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.
class TestAuthenticatedLogin(TestCase):
    """Test functionality of login page with valid uname/pwd."""
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user('testuser', 'test@test.org', 'testpwd') #type:ignore
        return super().setUpTestData()

    def test_login_redirect_to_dash(self):
        res = self.client.post('/login/', dict(username='testuser', password='testpwd'))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, '/dash/')

class TestUnauthenticatedLogin(TestCase):
    """Test functionality of login page with invalid uname/pwd."""
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user('testuser', 'test@test.org', 'testpwd') #type:ignore
        return super().setUpTestData()

    def test_wrong_password_unable_to_login(self):
        res = self.client.post('/login/', dict(username='testuser', password='WRONGpwd'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'].errors)

    def test_wrong_username_unable_to_login(self):
        res = self.client.post('/login/', dict(username='WRONGuser', password='WRONGpwd'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.context['form'].errors)

class TestLogout(TestCase):
    '''Test functionality of logout page.'''
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user('testuser', 'test@test.org', 'testpwd') #type:ignore
        return super().setUpTestData()

    def test_logout_cant_get_back_in(self):
        res = self.client.post('/login/', dict(username='testuser', password='testpwd'))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, '/dash/')
        res = self.client.get('/logout/')
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, '/')
        res = self.client.get('/dash/')
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, '/login/?next=/dash/')