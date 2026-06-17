from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тесты маршрутов"""
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='password'
        )
        cls.reader = User.objects.create_user(
            username='reader',
            password='password'
        )
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author,
        )

    def test_home_page_available_for_anonymous_user(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_for_authenticated_user(self):
        self.client.force_login(self.author)

        urls = (
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_access(self):
        test_cases = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        )

        for user, expected_status in test_cases:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirect_anonymous_user(self):
        login_url = reverse('users:login')

        for url in (
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{login_url}?next={url}")

    def test_auth_pages_available_for_all_users(self):
        urls = (
            reverse('users:signup'),
            reverse('users:login'),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
