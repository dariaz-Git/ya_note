from .confest import WithNoteMixin
from notes.forms import NoteForm


class TestContent(WithNoteMixin):

    def test_pages_contains_form(self):
        urls = (self.url_add, self.url_edit)
        self.client.force_login(self.author)
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_notes_list_for_different_users(self):
        # Зачем делить, если можно и объединёнными
        users = (
            (self.author, True),
            (self.reader, False)
        )
        for user, bool_stat in users:
            self.client.force_login(user)
            response = self.client.get(self.url_list)
            object_list = response.context['object_list']
            self.assertEqual(bool(self.note in object_list), bool_stat)
            if bool_stat:
                self.assertEqual(object_list.get(), self.note)
