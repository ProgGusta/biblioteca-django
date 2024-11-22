from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Colecao
from rest_framework.authtoken.models import Token

class ColecaoTests(APITestCase):
    def create_user_and_set_token_credentials(self):
        user = User.objects.create_user(
            "user01", "user01@example.com", "user01P4ssw0rD"
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))

    def setUp(self):
        self.create_user_and_set_token_credentials()
        '''
            self.user = User.objects.create_user(username='testuser', password='testpass')
            self.client.login(username='testuser', password='testpass')
        '''    

    def test_create_colecao(self):
        url = '/api/colecoes/'
        data = {'nome': 'Minha Coleção'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Colecao.objects.count(), 1)
        self.assertEqual(Colecao.objects.get().colecionador, self.user)

    def test_only_owner_can_edit_or_delete_colecao(self):
        colecao = Colecao.objects.create(nome='Minha Coleção', colecionador=self.user)
        url = f'/api/colecoes/{colecao.id}/'
        data = {'nome': 'Coleção Editada'}

        # Outro usuário tentando editar
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Outro usuário tentando deletar
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Proprietário editando
        self.client.login(username='testuser', password='testpass')
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Proprietário deletando
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_user_cannot_create_update_delete_colecao(self):
        self.client.logout()
        url = '/api/colecoes/'
        data = {'nome': 'Minha Coleção'}

        # Tentando criar
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Tentando editar
        colecao = Colecao.objects.create(nome='Minha Coleção', colecionador=self.user)
        url = f'/api/colecoes/{colecao.id}/'
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Tentando deletar
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_colecoes(self):
        Colecao.objects.create(nome='Coleção 1', colecionador=self.user)
        Colecao.objects.create(nome='Coleção 2', colecionador=self.user)
        url = '/api/colecoes/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)