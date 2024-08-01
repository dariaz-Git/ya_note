from .confest import URLS, WithNoteMixin
from notes.forms import NoteForm


class TestContent(WithNoteMixin):

    def test_pages_contains_form(self):
        urls = (URLS['add'], URLS['edit'])
        self.client.force_login(self.author)
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_notes_list_for_different_users(self):
        users = (
            (self.author, True),
            (self.reader, False)
        )
        for user, bool_stat in users:
            self.client.force_login(user)
            response = self.client.get(URLS['list'])
            object_list = response.context['object_list']
        self.assertEqual(bool(self.note in object_list), bool_stat)
