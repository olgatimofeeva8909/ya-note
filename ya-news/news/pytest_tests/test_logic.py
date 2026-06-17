from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(
        url,
        data={'text': 'Тестовый комментарий'},
    )
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
        author_client,
        news
):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(
        url,
        data={'text': 'Тестовый комментарий'},
    )
    assert response.status_code == HTTPStatus.FOUND


def test_comment_with_forbidden_words_not_published(
        author_client,
        news,
):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(
        url,
        data={'text': 'редиска'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors

@pytest.mark.parametrize(
    'url_name',
    (
        'news:edit',
        'news:delete',
    )
)
def test_author_can_edit_or_delete_own_comment(
        author_client,
        comment,
        url_name,
):
    url = reverse(
        url_name,
        args=(comment.id,)
    )
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name',
    (
        'news:edit',
        'news:delete',
    )
)
def test_user_cant_edit_or_delete_foreign_comment(
        reader_client,
        comment,
        url_name,
):
    url = reverse(
        url_name,
        args=(comment.id,)
    )
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
