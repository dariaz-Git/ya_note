from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Someone')
        cls.anotheruser = User.objects.create(username='Someoneelse')
        cls.slug_name = 'helping'
        cls.note = Note.objects.create(
            title='Название',
            text='Текст',
            slug=cls.slug_name,
            author=cls.author
        )

    def test_page_avaibility_for_anonymous_user(self):
        urls = (
            'notes:home', 'users:login',
            'users:logout', 'users:signup'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            'notes:list', 'notes:add', 'notes:success'
        )
        user = self.anotheruser
        self.client.force_login(user)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_avaibility_for_different_users(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.anotheruser, HTTPStatus.NOT_FOUND)
        )
        urls = (
            'notes:detail', 'notes:edit', 'notes:delete'
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_not_authenticated(self):
        urls = (
            ('notes:detail', self.note.slug),
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None)
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                if args is not None:
                    url = reverse(name, args=(args,))
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
