from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Colecao
from rest_framework.authtoken.models import Token

class ColecaoTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def post_colecao(self, nome):
        url = reverse('colecao-list-create')
        data = {'nome': nome}
        response = self.client.post(url, data, format='json')
        return response

    def test_criar_colecao(self):
        response = self.post_colecao('Minha Coleção')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Colecao.objects.count(), 1)
        self.assertEqual(Colecao.objects.get().colecionador, self.user)

    def test_apenas_colecionador_pode_editar_ou_deletar_colecao(self):
        colecao = Colecao.objects.create(nome='Minha Coleção', colecionador=self.user)
        url = reverse('colecao-detail', args=[colecao.id])
        data = {'nome': 'Coleção Editada'}
        
        # Teste de edição pelo colecionador
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Colecao.objects.get().nome, 'Coleção Editada')
        
        # Teste de edição por outro usuário
        outro_usuario = User.objects.create_user(username='outro', password='testpass')
        outro_token = Token.objects.create(user=outro_usuario)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + outro_token.key)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Teste de deleção pelo colecionador
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Colecao.objects.count(), 0)

    def test_usuario_nao_autenticado_nao_pode_criar_colecao(self):
        self.client.logout()
        url = reverse('colecao-list-create')
        data = {'nome': 'Minha Coleção'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_usuario_nao_autenticado_nao_pode_atualizar_colecao(self):
        colecao = Colecao.objects.create(nome='Minha Coleção', colecionador=self.user)
        self.client.logout()
        url = reverse('colecao-detail', args=[colecao.id])
        response = self.client.put(url, {'nome': 'Coleção Editada'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_usuario_nao_autenticado_nao_pode_deletar_colecao(self):
        colecao = Colecao.objects.create(nome='Minha Coleção', colecionador=self.user)
        self.client.logout()
        url = reverse('colecao-detail', args=[colecao.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listagem_colecoes_visiveis_para_usuarios_autenticados(self):
        Colecao.objects.create(nome='Coleção 1', colecionador=self.user)
        Colecao.objects.create(nome='Coleção 2', colecionador=self.user)
        
        url = reverse('colecao-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)