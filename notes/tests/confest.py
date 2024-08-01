from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()
TITLE = 'name'
TEXT = 'Старый текст'
NEW_TEXT = 'Новый текст'
FORM_DATA = {'title': TITLE, 'text': TEXT}
URLS = {
    'home': reverse('notes:home'),
    'login': reverse('users:login'),
    'logout': reverse('users:logout'),
    'signup': reverse('users:signup'),
    'success': reverse('notes:success'),
    'list': reverse('notes:list'),
    'add': reverse('notes:add'),
    'detail': reverse('notes:detail', args=(TITLE,)),
    'edit': reverse('notes:edit', args=(TITLE,)),
    'delete': reverse('notes:delete', args=(TITLE,))
}


class WithNoteMixin(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Автор
        cls.author = User.objects.create(username='Writer')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        # Читатель
        cls.reader = User.objects.create(username='Someoneelse')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=TITLE,
            text=TEXT,
            author=cls.author
        )


class WithoutNoteMixin(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Writer')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
