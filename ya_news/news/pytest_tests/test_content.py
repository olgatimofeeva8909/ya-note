from datetime import timedelta

import pytest

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import News, Comment


@pytest.fixture
@pytest.mark.django_db
def news():
    today = timezone.now().date()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)]
    News.objects.bulk_create(news_list)
    return news_list


@pytest.mark.django_db
def test_news_count(client, news):
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['object_list']
    assert (news_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE)


@pytest.mark.django_db
def test_news_order(client, news):
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['object_list']
    dates = [item.date for item in news_list]
    assert dates == sorted(dates, reverse=True)


@pytest.fixture
@pytest.mark.django_db
def detail_news():
    return News.objects.create(
        title='Новость',
        text='Текст'
    )


@pytest.fixture
@pytest.mark.django_db
def comment_news(detail_news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=detail_news,
            author=author,
            text=f'Текст {index}'
        )
        comment.created = (now + timedelta(days=index))
        comment.save()
    return detail_news


@pytest.mark.django_db
def test_comments_order(client, comment_news):
    url = reverse('news:detail', args=(comment_news.id,))
    response = client.get(url)
    news = response.context['news']
    comments = news.comment_set.all()
    dates = [comment.created for comment in comments]
    assert dates == sorted(dates)


@pytest.mark.django_db
def test_anonymous_user_cant_see_comment_form(client, detail_news):
    url = reverse('news:detail', args=(detail_news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_user_can_see_comment_form(author_client, detail_news):
    url = reverse('news:detail', args=(detail_news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
