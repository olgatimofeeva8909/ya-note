from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='author',
            password='password'
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
            'slug': 'new-slug',
        }
        cls.note = Note.objects.create(
            title='Существующая заметка',
            text='Текст',
            slug='test-slug',
            author=cls.user,
        )

    def test_auth_user_can_create_note(self):
        notes_count = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count + 1)

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_cannot_create_note_with_duplicate_slug(self):
        notes_count = Note.objects.count()
        self.auth_client.post(
            self.url,
            data={
                'title': 'Другая заметка',
                'text': 'Другой текст',
                'slug': self.note.slug,
            }
        )
        self.assertEqual(Note.objects.count(), notes_count)

    def test_empty_slug_auto_generated(self):
        self.auth_client.post(
            self.url,
            data={
                'title': 'Слаг',
                'text': 'Текст заметки',
                'slug': '',
            }
        )
        note = Note.objects.get(title='Слаг')
        self.assertEqual(note.slug, slugify('Слаг'))


class TestNoteEditDelete(TestCase):

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
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author,
        )

    def test_author_can_edit_note(self):
        self.author_client.post(
            reverse('notes:edit', args=(self.note.slug,)),
            data={
                'title': 'Отредактированная заметка',
                'text': 'Новый текст',
                'slug': self.note.slug,
            }
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Отредактированная заметка')
        self.assertEqual(self.note.text, 'Новый текст')

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        self.author_client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_other_user_cant_edit_note(self):
        self.reader_client.post(
            reverse('notes:edit', args=(self.note.slug,)),
            data={
                'title': 'Попытка изменить',
                'text': 'Новый текст',
                'slug': self.note.slug,
            }
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Тестовая заметка')
        self.assertEqual(self.note.text, 'Текст заметки')

    def test_other_user_cant_delete_note(self):
        notes_count = Note.objects.count()
        self.reader_client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertEqual(Note.objects.count(), notes_count)
