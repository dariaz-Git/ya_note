from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Someone')
        cls.url_add = reverse('notes:add', args=None)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.url_add)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
    # Для анонимного с 'form' не работает, а проверка на редирект уже была
