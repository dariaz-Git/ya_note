from http import HTTPStatus

from pytils.translit import slugify

from .confest import (
    FORM_DATA, FORM_DATA_SLUG, NEW_FORM_DATA, NEW_TEXT, TEXT, TITLE,
    WithNoteMixin
)
from notes.forms import WARNING
from notes.models import Note


class TestNoteCreationDeleteEdit(WithNoteMixin):

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url_add, data=FORM_DATA)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_create_note(self):
        response = self.author_client.post(self.url_add, data=FORM_DATA_SLUG)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 2)
        note = Note.objects.get(slug=FORM_DATA_SLUG['slug'])
        self.assertEqual(note.title, TITLE)
        self.assertEqual(note.text, TEXT)
        self.assertEqual(note.author, self.author)

    def test_empty_slug(self):
        expected_slug = slugify(TITLE)
        self.assertEqual(self.note.slug, expected_slug)

    def test_uniqueness_of_slug(self):
        response = self.reader_client.post(self.url_add, data=FORM_DATA)
        self.assertFormError(
            response, 'form', 'slug', errors=(
                Note.objects.get().slug + WARNING
            )
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_strangers_note(self):
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.title, TITLE)
        self.assertEqual(note.text, TEXT)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.url_edit, data=NEW_FORM_DATA
        )
        self.assertRedirects(response, self.url_success)
        note = Note.objects.get()
        self.assertEqual(note.text, NEW_TEXT)
        self.assertEqual(note.title, TITLE)
        self.assertEqual(note.author, self.author)

    def test_reader_cant_edit_strangers_note(self):
        response = self.reader_client.post(self.url_edit, data=FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get()
        self.assertEqual(note.text, TEXT)
        self.assertEqual(note.title, TITLE)
        self.assertEqual(note.author, self.author)
