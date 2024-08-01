from http import HTTPStatus

from pytils.translit import slugify

from .confest import (
    FORM_DATA, NEW_TEXT, TEXT, TITLE, URLS, WithNoteMixin, WithoutNoteMixin
)
from notes.forms import WARNING
from notes.models import Note


class TestNoteCreation(WithoutNoteMixin):

    def test_anonymous_user_cant_create_note(self):
        self.client.post(URLS['add'], data=FORM_DATA)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.author_client.post(URLS['add'], data=FORM_DATA)
        self.assertRedirects(response, URLS['success'])
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.assertEqual(Note.objects.get().title, TITLE)
        self.assertEqual(Note.objects.get().text, TEXT)
        self.assertEqual(Note.objects.get().author, self.author)


class TestNoteEditDeleteAndSlug(WithNoteMixin):

    def test_empty_slug(self):
        expected_slug = slugify(TITLE)
        self.assertEqual(self.note.slug, expected_slug)

    def test_uniqueness_of_slug(self):
        response = self.reader_client.post(URLS['add'], data=FORM_DATA)
        self.assertFormError(
            response, 'form', 'slug', errors=(
                Note.objects.get().slug + WARNING
            )
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(URLS['delete'])
        self.assertRedirects(response, URLS['success'])
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_strangers_note(self):
        response = self.reader_client.delete(URLS['delete'])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        new_form_data = {'title': TITLE, 'text': NEW_TEXT}
        response = self.author_client.post(
            URLS['edit'], data=new_form_data
        )
        self.assertRedirects(response, URLS['success'])
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, NEW_TEXT)

    def test_reader_cant_edit_strangers_note(self):
        response = self.reader_client.post(URLS['edit'], data=FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, TEXT)
