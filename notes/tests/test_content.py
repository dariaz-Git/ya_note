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

    # Эхх, разделить так разделить(
    def test_notes_list_for_not_author(self):
        response = self.reader_client.get(self.url_list)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_notes_list_for_author(self):
        response = self.author_client.get(self.url_list)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertEqual(object_list.get(), self.note)
