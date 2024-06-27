from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()
TITLE = 'Name'
TEXT = 'Старый текст'
NEW_TEXT = 'Новый текст'


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.form_data = {'title': TITLE, 'text': TEXT}
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='The Writer')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

    def test_anonymous_user_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    # Надо поправить
    def test_uniqueness_of_slug(self):
        # Создаю первый и проверяю, что он появился
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.auth_client.post(self.url, data=self.form_data)
        # Работа со вторым
        with self.assertRaises(ValidationError):
            self.auth_client.post(self.url, data=self.form_data)
        # Тест на raise не проходит
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        # Второй точно не создаётся: тест пройден


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Note`s Writer')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=TITLE,
            text=TEXT,
            slug='name',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.done_url = reverse('notes:success')
        cls.form_data = {'title': TEXT, 'text': NEW_TEXT}

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
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, NEW_TEXT)

    def test_reader_cant_edit_strangers_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, TEXT)
