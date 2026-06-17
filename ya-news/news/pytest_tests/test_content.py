from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_news_count_on_homepage(client):
    url = reverse('news:home')
    response = client.get(url)
    assert len(response.context['object_list']) <= 10


@pytest.mark.django_db
def test_news_order_on_homepage(client):
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['object_list']
    dates = [item.date for item in news_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order_on_detail_page(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    comments = response.context['news'].comment_set.all()
    dates = [comment.created for comment in comments]
    assert dates == sorted(dates)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture, expected_result',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('anonymous_client'), False),
    )
)
def test_comment_form_availability(
    client_fixture,
    expected_result,
    news,
):
    url = reverse('news:detail', args=(news.id,))
    response = client_fixture.get(url)
    assert (response.context.get('form') is not None) == expected_result
