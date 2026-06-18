
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestContent(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            password='password'
        )
        self.reader = User.objects.create_user(
            username='reader',
            password='password'
        )
        self.note = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug='slug',
            author=self.author
        )
        self.author_client = Client()
        self.reader_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client.force_login(self.reader)

    def test_note_in_list_for_author(self):
        response = self.author_client.get(
            reverse('notes:list')
        )
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_other_user(self):
        response = self.reader_client.get(
            reverse('notes:list')
        )
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_page_contains_form(self):
        response = self.author_client.get(
            reverse('notes:add')
        )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_contains_form(self):
        response = self.author_client.get(
            reverse('notes:edit', args=(self.note.slug,)))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
