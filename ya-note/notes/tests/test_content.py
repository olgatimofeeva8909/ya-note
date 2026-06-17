from django.contrib.auth import get_user_model
from django.test import TestCase

from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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
        cls.other_note = Note.objects.create(
            title='Заметка другого пользователя',
            text='Текст заметки',
            author=cls.reader,
        )

    def test_notes_list_only_author_notes(self):
        self.client.force_login(self.author)

        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']

        self.assertIn(self.note, object_list)
        self.assertNotIn(self.other_note, object_list)

    def test_forms_in_create_and_edit_pages(self):
        self.client.force_login(self.author)

        for url in (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
