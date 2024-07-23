from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()
TITLE = 'Name'
TEXT = 'Старый текст'
NEW_TEXT = 'Новый текст'
FORM_DATA = {'title': TITLE, 'text': TEXT}


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='The Writer')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=FORM_DATA)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=FORM_DATA)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.assertEqual(Note.objects.get().title, TITLE)
        self.assertEqual(Note.objects.get().text, TEXT)
        self.assertEqual(Note.objects.get().author, self.user)


class TestNoteEditDeleteAndSlug(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Автор
        cls.author = User.objects.create(username='Note`s Writer')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        # Читатель
        cls.reader = User.objects.create(username='Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Остальные вводные
        cls.note = Note.objects.create(
            title=TITLE,
            text=TEXT,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.done_url = reverse('notes:success')

    def test_empty_slug(self):
        expected_slug = slugify(FORM_DATA['title'])
        self.assertEqual(self.note.slug, expected_slug)

    def test_uniqueness_of_slug(self):
        # Работа со вторым
        url = reverse('notes:add')
        response = self.reader_client.post(url, data=FORM_DATA)
        self.assertFormError(
            response, 'form', 'slug', errors=(
                Note.objects.get().slug + WARNING
            )
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_strangers_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        new_form_data = {'title': TITLE, 'text': NEW_TEXT}
        response = self.author_client.post(self.edit_url, data=new_form_data)
        self.assertRedirects(response, self.done_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, NEW_TEXT)

    def test_reader_cant_edit_strangers_note(self):
        response = self.reader_client.post(self.edit_url, data=FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, TEXT)
