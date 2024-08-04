from http import HTTPStatus

from pytils.translit import slugify

from .confest import (
    FORM_DATA, NEW_FORM_DATA, NEW_TEXT, TEXT, TITLE,
    WithNoteMixin
)
from notes.forms import WARNING
from notes.models import Note


class TestNoteCreation(WithNoteMixin):

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url_add, data=FORM_DATA)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        FORM_DATA = {'title': TITLE, 'text': TEXT, 'slug': 'helloimslug'}
        response = self.author_client.post(self.url_add, data=FORM_DATA)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        note = Note.objects.get(slug=FORM_DATA['slug'])
        self.assertEqual(note.title, TITLE)
        self.assertEqual(note.text, TEXT)
        self.assertEqual(note.author, self.author)


class TestNoteEditDeleteAndSlug(WithNoteMixin):
    # Что стоит объявить в одном классе?
    # Если про Mixin, то они должны быть разделены

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
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_strangers_note(self):
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.url_edit, data=NEW_FORM_DATA
        )
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        note = Note.objects.get()
        self.assertEqual(note.text, NEW_TEXT)
        self.assertEqual(note.title, TITLE)
        self.assertEqual(note.author, self.author)

    def test_reader_cant_edit_strangers_note(self):
        response = self.reader_client.post(self.url_edit, data=FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        note = Note.objects.get()
        self.assertEqual(note.text, TEXT)
        self.assertEqual(note.title, TITLE)
        self.assertEqual(note.author, self.author)
