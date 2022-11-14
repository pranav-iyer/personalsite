from django.test import TestCase
from django.contrib.auth.models import User
from groceries.models import GList

#ALTER USER django CREATEDB; === comment to make user able to run tests

# Create your tests here.
class URLPingTest(TestCase):
    """Ensure that, once logged in, pages are giving a successful 200 status code."""
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user('testuser', 'test@test.org', 'testpwd') #type:ignore
        GList.objects.create(title="My List")
        return super().setUpTestData()

    def setUp(self) -> None:
        self.client.login(username="testuser", password="testpwd")
        return super().setUp()

    def test_index(self):
        res = self.client.get("/gman/", follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.redirect_chain[-1][0], '/gman/glist/active/')

    def test_all_list(self):
        res = self.client.get("/gman/glist/all/")
        self.assertEqual(res.status_code, 200)

    def test_active_list(self):
        res = self.client.get("/gman/glist/active/")
        self.assertEqual(res.status_code, 200)

    def test_add(self):
        res = self.client.get("/gman/glist/add/", follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.redirect_chain[-1][0], '/gman/glist/2/')

    def test_edit(self):
        res = self.client.get("/gman/glist/1/")
        self.assertEqual(res.status_code, 200)

    def test_shopping(self):
        res = self.client.get("/gman/glist/1/shopping/")
        self.assertEqual(res.status_code, 200)

    def test_store_select(self):
        res = self.client.get("/gman/glist/1/store-select/")
        self.assertEqual(res.status_code, 200)

    def test_trip(self):
        res = self.client.get("/gman/glist/1/trip/")
        self.assertEqual(res.status_code, 200)

class LoginProtectedTest(TestCase):
    """Ensures that all URLs in GMan are not accessible to a non-authenticated user. 
    Each URL should redirect to the login page, with a next value pointing to the
    desired URL."""

    def setUp(self) -> None:
        self.url_list = ['glist/all/', 'glist/active/', 'glist/add/',
            'glist/0/shopping/', 'glist/0/trip/', 'glist/0/', 'glist/0/store-select/',
            'glist/0/delete/', '']
        return super().setUp()

    def test_urls_protected(self):
        for url in self.url_list:
            with self.subTest(msg=f"Checking URL {url}"):
                url_path = '/gman/' + url
                res = self.client.get(url_path)
                self.assertEqual(res.status_code, 302)
                self.assertEqual(res.url, f"/login/?next={url_path}")
