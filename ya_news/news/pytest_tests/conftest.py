import pytest

from django.test import Client
from django.contrib.auth import get_user_model

from news.models import News, Comment


User = get_user_model()


@pytest.fixture
@pytest.mark.django_db
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
@pytest.mark.django_db
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст'
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
