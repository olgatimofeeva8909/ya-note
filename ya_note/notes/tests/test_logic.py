from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from pytils.translit import slugify

from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestLogic(TestCase):

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
        self.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        self.author_client = Client()
        self.reader_client = Client()
        self.client = Client()
        self.author_client.force_login(self.author)
        self.reader_client.force_login(self.reader)

    def test_user_can_create_note(self):
        response = self.author_client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(slug='new-slug')
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        data = self.form_data.copy()
        data['slug'] = self.note.slug
        response = self.author_client.post(
            reverse('notes:add'),
            data=data
        )
        self.assertFormError(
            response.context['form'],
            'slug', self.note.slug + WARNING)
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        data = self.form_data.copy()
        data.pop('slug')
        response = self.author_client.post(
            reverse('notes:add'),
            data=data
        )
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get(title=data['title'])
        expected_slug = slugify(data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            reverse(
                'notes:edit',
                args=(self.note.slug,)
            ),
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(
            reverse('notes:edit', args=(self.note.slug,)),
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Заметка')
        self.assertEqual(self.note.text, 'Текст заметки')
        self.assertEqual(self.note.slug, 'slug')

    def test_author_can_delete_note(self):
        response = self.author_client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.reader_client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
