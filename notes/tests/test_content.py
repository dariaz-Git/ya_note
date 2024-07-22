from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Writer')
        cls.anotheruser = User.objects.create(username='Someoneelse')
        cls.slug_name = 'helping'
        cls.note = Note.objects.create(
            title='Название',
            text='Текст',
            slug=cls.slug_name,
            author=cls.author
        )

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.slug_name,))
        )
        self.client.force_login(self.author)
        for name, arg in urls:
            with self.subTest(name=name):
                url = reverse(name, args=arg)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_notes_list_for_different_users(self):
        url = reverse('notes:list')
        users = (
            (self.author, True),
            (self.anotheruser, False)
        )
        for user, bool_stat in users:
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context['object_list']
        self.assertEqual(bool(self.note in object_list), bool_stat)
