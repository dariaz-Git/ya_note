from http import HTTPStatus

from .confest import WithNoteMixin


class TestRoutes(WithNoteMixin):

    def test_page_aviability(self):
        cases = [
            [self.author_client, self.url_detail, HTTPStatus.OK],
            [self.author_client, self.url_edit, HTTPStatus.OK],
            [self.author_client, self.url_delete, HTTPStatus.OK],
            [self.author_client, self.url_list, HTTPStatus.OK],
            [self.author_client, self.url_add, HTTPStatus.OK],
            [self.author_client, self.url_success, HTTPStatus.OK],
            [self.reader_client, self.url_detail, HTTPStatus.NOT_FOUND],
            [self.reader_client, self.url_edit, HTTPStatus.NOT_FOUND],
            [self.reader_client, self.url_delete, HTTPStatus.NOT_FOUND],
            [self.client, self.url_home, HTTPStatus.OK],
            [self.client, self.url_login, HTTPStatus.OK],
            [self.client, self.url_logout, HTTPStatus.OK],
            [self.client, self.url_signup, HTTPStatus.OK],
            [self.client, self.url_detail, HTTPStatus.FOUND],
            [self.client, self.url_edit, HTTPStatus.FOUND],
            [self.client, self.url_delete, HTTPStatus.FOUND],
            [self.client, self.url_add, HTTPStatus.FOUND],
            [self.client, self.url_success, HTTPStatus.FOUND],
            [self.client, self.url_list, HTTPStatus.FOUND],
        ]
        for user, url, status in cases:
            with self.subTest(user=user, name=url):
                response = user.get(url)
                self.assertEqual(response.status_code, status)
                if status == HTTPStatus.FOUND:
                    redirect_url = f'{self.url_login}?next={url}'
                    self.assertRedirects(response, redirect_url)
