from http import HTTPStatus

import pytest

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data={'text': 'Комментарий'})
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data={'text': 'Комментарий'})
    assert response.status_code == HTTPStatus.FOUND
    comment = Comment.objects.get()
    assert comment.text == 'Комментарий'
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data={'text': f'Текст {BAD_WORDS[0]}'})
    form = response.context['form']
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data={'text': 'Обновлённый комментарий'})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == 'Обновлённый комментарий'


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, data={'text': 'Другой текст'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
