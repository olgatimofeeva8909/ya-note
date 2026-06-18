from http import HTTPStatus

import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    (
        'news:home',
        'users:login',
        'users:signup',
    )
)
@pytest.mark.django_db
def test_pages_availability(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('author_client'),HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'),HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',)
)
def test_comment_pages(
        parametrized_client,
        status,
        name,
        comment
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',)
)
@pytest.mark.django_db
def test_redirect_anonymous(client, comment, name):
    url = reverse(name, args=(comment.id,))
    login_url = reverse('users:login')
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')
