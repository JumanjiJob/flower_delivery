from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from .forms import UserRegisterForm


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_profile_creation(self):
        """Тест автоматического создания профиля при создании пользователя"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)

    def test_profile_str(self):
        """Тест строкового представления профиля"""
        expected_str = f"{self.user.username} - {self.user.profile.phone}"
        self.assertEqual(str(self.user.profile), expected_str)


class UserRegisterFormTest(TestCase):
    def test_valid_registration_form(self):
        """Тест валидной формы регистрации"""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_registration_form(self):
        """Тест невалидной формы регистрации"""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
            'password1': 'complexpassword123',
            'password2': 'differentpassword',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_register_view_get(self):
        """Тест GET запроса к странице регистрации"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertContains(response, 'Регистрация')

    def test_register_view_post(self):
        """Тест POST запроса к странице регистрации"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        })
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        """Тест GET запроса к странице входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_view_post(self):
        """Тест успешного входа"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # redirect after login

    def test_profile_view_authenticated(self):
        """Тест доступа к профилю для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_view_unauthenticated(self):
        """Тест редиректа для неавторизованного пользователя"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_logout_view(self):
        """Тест выхода из системы"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/logout.html')


class URLTests(TestCase):
    def test_urls(self):
        """Тест доступности URL-адресов"""
        urls = [
            reverse('register'),
            reverse('login'),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)