from http import HTTPStatus

from .confest import URLS, WithNoteMixin


class TestRoutes(WithNoteMixin):

    def test_page_avaibility_for_anonymous_user(self):
        urls = (
            URLS['home'], URLS['login'],
            URLS['logout'], URLS['signup']
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            URLS['list'], URLS['add'], URLS['success']
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_avaibility_for_different_users(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND)
        )
        urls = (
            URLS['detail'], URLS['edit'], URLS['delete']
        )
        for user, status in users_statuses:
            for url in urls:
                with self.subTest(name=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_not_authenticated(self):
        urls = (
            URLS['detail'],
            URLS['edit'],
            URLS['delete'],
            URLS['add'],
            URLS['success'],
            URLS['list']
        )
        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{URLS["login"]}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
