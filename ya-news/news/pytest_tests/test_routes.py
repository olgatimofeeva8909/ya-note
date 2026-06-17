from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_news_available_for_anonymous_user(client, news):
    url = reverse(
        'news:detail',
        args=(news.id,)
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    (
        'news:edit',
        'news:delete',
    )
)
def test_author_can_manage_comment(author_client, comment, url_name):
    url = reverse(url_name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    (
        'news:edit',
        'news:delete',
    )
)
def test_anonymous_user_redirected_to_login(client, comment, url_name):
    url = reverse(
        url_name,
        args=(comment.id,)
    )
    response = client.get(url)
    login_url = reverse('users:login')
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{login_url}?next={url}'


@pytest.mark.django_db
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
        url_name
):
    url = reverse(
        url_name,
        args=(comment.id,)
    )
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('users:signup', 'users:login')
)
def test_auth_pages_available_for_anonymous(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_available(client):
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK
