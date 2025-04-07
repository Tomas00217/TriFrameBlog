from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class LoginViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")

    def test_login_view(self):
        """
        User login
        """
        response = self.client.post(reverse("login"), {
            "email": self.user.email,
            "password": "password"
        })
        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertRedirects(response, "/")

    def test_login_invalid_credentials(self):
        """
        Login with invalid credentials
        """
        response = self.client.post(reverse("login"), {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        self.assertFalse("_auth_user_id" in self.client.session)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your email and password did not match. Please try again.")

class RegisterViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")

    def test_register_view(self):
        """
        User registration
        """
        response = self.client.post(reverse("register"), {
            "email": "newuser@example.com",
            "password1": "Testpassword123!",
            "password2": "Testpassword123!",
        })
        self.assertTrue(get_user_model().objects.filter(email="newuser@example.com").exists())
        self.assertRedirects(response, "/accounts/login/")

    def test_register_passwords_dont_match(self):
        """
        User registration with not matching passwords
        """
        response = self.client.post(reverse("register"), {
            "email": "newuser@example.com",
            "password1": "Testpassword123!",
            "password2": "WrongSecondPass123.",
        })
        self.assertFalse(get_user_model().objects.filter(email="newuser@example.com").exists()) 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match.") 

    def test_register_email_exists(self):
        """
        User registration with existing email account
        """
        response = self.client.post(reverse("register"), {
            "email": "user@example.com",
            "password1": "Testpassword123!",
            "password2": "Testpassword123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email user with this Email already exists.")

class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")

    def test_profile_view_requires_login(self):
        """
        Unauthenticated user is redirected to login.
        """
        response = self.client.get(reverse("profile"))
        self.assertRedirects(response, "/accounts/login/?next=/accounts/profile/")

    def test_profile_update(self):
        """
        Updating username
        """
        self.client.login(email="user@example.com", password="password")
        response = self.client.post(reverse("profile"), {"username": "updateduser"})
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")