from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Usuario, Operacao
import json


class TemplateViewsTestCase(TestCase):
    """Testes para as views que servem templates HTML."""
    
    def setUp(self):
        self.client = Client()
        
    def test_login_view_get(self):
        """Testa se a página de login é carregada corretamente."""
        response = self.client.get(reverse('calculadora:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')
        
    def test_login_view_root_url(self):
        """Testa se a URL raiz redireciona para login."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_calculadora_view_get(self):
        """Testa se a página da calculadora é carregada."""
        response = self.client.get(reverse('calculadora:calculadora'))
        self.assertEqual(response.status_code, 200)
        
    def test_perfil_view_get(self):
        """Testa se a página de perfil é carregada."""
        response = self.client.get(reverse('calculadora:perfil'))
        self.assertEqual(response.status_code, 200)


class RegistroAPITestCase(APITestCase):
    """Testes para a API de registro de usuários."""
    
    def setUp(self):
        self.url = reverse('calculadora:api_registro')
        self.valid_data = {
            'nome': 'Teste Usuario',
            'email': 'teste@exemplo.com',
            'senha': 'senha123456',
            'confirmar_senha': 'senha123456'
        }
        
    def test_registro_sucesso(self):
        """Testa registro de usuário com dados válidos."""
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertTrue(response.data['authenticated'])
        
    def test_registro_email_duplicado(self):
        """Testa registro com email já existente."""
        # Criar primeiro usuário
        Usuario.objects.create_user(
            username='teste1',
            email='teste@exemplo.com',
            password='senha123'
        )
        
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_registro_senhas_diferentes(self):
        """Testa registro com senhas que não coincidem."""
        data = self.valid_data.copy()
        data['confirmar_senha'] = 'outrasenha'
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_registro_dados_invalidos(self):
        """Testa registro com dados inválidos."""
        data = {
            'nome': '',
            'email': 'email_invalido',
            'senha': '123',
            'confirmar_senha': '123'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITestCase(APITestCase):
    """Testes para a API de login."""
    
    def setUp(self):
        self.url = reverse('calculadora:api_login')
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='teste@exemplo.com',
            password='senha123456',
            nome='Teste Usuario'
        )
        
    def test_login_sucesso(self):
        """Testa login com credenciais válidas."""
        data = {
            'email': 'teste@exemplo.com',
            'senha': 'senha123456'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('usuario', response.data)
        self.assertTrue(response.data['authenticated'])
        
    def test_login_credenciais_invalidas(self):
        """Testa login com credenciais inválidas."""
        data = {
            'email': 'teste@exemplo.com',
            'senha': 'senhaerrada'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_login_email_inexistente(self):
        """Testa login com email que não existe."""
        data = {
            'email': 'inexistente@exemplo.com',
            'senha': 'senha123456'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutAPITestCase(APITestCase):
    """Testes para a API de logout."""
    
    def setUp(self):
        self.url = reverse('calculadora:api_logout')
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='teste@exemplo.com',
            password='senha123456',
            nome='Teste Usuario'
        )
        
    def test_logout_autenticado(self):
        """Testa logout com usuário autenticado."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertFalse(response.data['authenticated'])
        
    def test_logout_nao_autenticado(self):
        """Testa logout sem autenticação."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PerfilAPITestCase(APITestCase):
    """Testes para a API de perfil do usuário."""
    
    def setUp(self):
        self.url = reverse('calculadora:api_perfil')
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='teste@exemplo.com',
            password='senha123456',
            nome='Teste Usuario'
        )
        
    def test_get_perfil_autenticado(self):
        """Testa obtenção do perfil com usuário autenticado."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'teste@exemplo.com')
        self.assertEqual(response.data['nome'], 'Teste Usuario')
        
    def test_update_perfil_autenticado(self):
        """Testa atualização do perfil com usuário autenticado."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'nome': 'Nome Atualizado',
            'email': 'novo@exemplo.com'
        }
        
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Nome Atualizado')
        
    def test_perfil_nao_autenticado(self):
        """Testa acesso ao perfil sem autenticação."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CalcularAPITestCase(APITestCase):
    """Testes para a API de cálculos matemáticos."""
    
    def setUp(self):
        self.url = reverse('calculadora:api_calcular')
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='teste@exemplo.com',
            password='senha123456',
            nome='Teste Usuario'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_calculo_soma(self):
        """Testa operação de soma."""
        data = {'operacao': '2 + 3'}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['resultado'], 5)
        self.assertEqual(response.data['operacao'], '2 + 3')
        
    def test_calculo_subtracao(self):
        """Testa operação de subtração."""
        data = {'operacao': '10 - 4'}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['resultado'], 6)
        
    def test_calculo_multiplicacao(self):
        """Testa operação de multiplicação."""
        data = {'operacao': '3 * 7'}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['resultado'], 21)
        
    def test_calculo_divisao(self):
        """Testa operação de divisão."""
        data = {'operacao': '15 / 3'}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['resultado'], 5)
        
    def test_calculo_parenteses(self):
        """Testa operação com parênteses."""
        data = {'operacao': '(2 + 3) * 4'}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['resultado'], 20)
        
    def test_calculo_divisao_por_zero(self):
        """Testa divisão por zero."""
        data = {'operacao': '5 / 0'}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('erro', response.data)
        
    def test_calculo_expressao_invalida(self):
        """Testa expressão matemática inválida."""
        data = {'operacao': '2 + + 3'}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_calculo_caracteres_invalidos(self):
        """Testa operação com caracteres não permitidos."""
        data = {'operacao': '2 + abc'}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_calculo_nao_autenticado(self):
        """Testa cálculo sem autenticação."""
        self.client.force_authenticate(user=None)
        data = {'operacao': '2 + 3'}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OperacoesListAPITestCase(APITestCase):
    """Testes para a API de listagem de operações."""
    
    def setUp(self):
        self.url = reverse('calculadora:api_operacoes')
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='teste@exemplo.com',
            password='senha123456',
            nome='Teste Usuario'
        )
        self.client.force_authenticate(user=self.user)
        
        # Criar algumas operações de teste
        Operacao.objects.create(
            usuario=self.user,
            operacao='2 + 3',
            resultado='5'
        )
        Operacao.objects.create(
            usuario=self.user,
            operacao='10 - 4',
            resultado='6'
        )
        
    def test_listar_operacoes_autenticado(self):
        """Testa listagem de operações com usuário autenticado."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_listar_operacoes_nao_autenticado(self):
        """Testa listagem de operações sem autenticação."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LimparHistoricoAPITestCase(APITestCase):
    """Testes para a API de limpeza de histórico."""
    
    def setUp(self):
        self.url = reverse('calculadora:api_limpar_historico')
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='teste@exemplo.com',
            password='senha123456',
            nome='Teste Usuario'
        )
        self.client.force_authenticate(user=self.user)
        
        # Criar operações de teste
        for i in range(3):
            Operacao.objects.create(
                usuario=self.user,
                operacao=f'{i} + 1',
                resultado=str(i + 1)
            )
            
    def test_limpar_historico_autenticado(self):
        """Testa limpeza de histórico com usuário autenticado."""
        # Verificar que existem operações
        self.assertEqual(Operacao.objects.filter(usuario=self.user).count(), 3)
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['operacoes_deletadas'], 3)
        
        # Verificar que as operações foram deletadas
        self.assertEqual(Operacao.objects.filter(usuario=self.user).count(), 0)
        
    def test_limpar_historico_nao_autenticado(self):
        """Testa limpeza de histórico sem autenticação."""
        self.client.force_authenticate(user=None)
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EstatisticasAPITestCase(APITestCase):
    """Testes para a API de estatísticas."""
    
    def setUp(self):
        self.url = reverse('calculadora:api_estatisticas')
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='teste@exemplo.com',
            password='senha123456',
            nome='Teste Usuario'
        )
        self.client.force_authenticate(user=self.user)
        
        # Criar operações de teste
        Operacao.objects.create(
            usuario=self.user,
            operacao='2 + 3',
            resultado='5'
        )
        
    def test_estatisticas_autenticado(self):
        """Testa obtenção de estatísticas com usuário autenticado."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar campos obrigatórios
        self.assertIn('total_operacoes', response.data)
        self.assertIn('operacoes_hoje', response.data)
        self.assertIn('operacoes_semana', response.data)
        self.assertIn('operacoes_por_tipo', response.data)
        self.assertIn('membro_desde', response.data)
        
        self.assertEqual(response.data['total_operacoes'], 1)
        
    def test_estatisticas_nao_autenticado(self):
        """Testa obtenção de estatísticas sem autenticação."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeletarContaAPITestCase(APITestCase):
    """Testes para a API de exclusão de conta."""
    
    def setUp(self):
        self.url = reverse('calculadora:api_deletar_conta')
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='teste@exemplo.com',
            password='senha123456',
            nome='Teste Usuario'
        )
        
    def test_deletar_conta_autenticado(self):
        """Testa exclusão de conta com usuário autenticado."""
        self.client.force_authenticate(user=self.user)
        user_id = self.user.id
        
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertFalse(response.data['authenticated'])
        
        # Verificar que o usuário foi deletado
        self.assertFalse(Usuario.objects.filter(id=user_id).exists())
        
    def test_deletar_conta_nao_autenticado(self):
        """Testa exclusão de conta sem autenticação."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class URLsTestCase(TestCase):
    """Testes para verificar se todas as URLs estão configuradas corretamente."""
    
    def test_urls_existem(self):
        """Testa se todas as URLs definidas existem e são acessíveis."""
        urls_to_test = [
            'calculadora:login',
            'calculadora:calculadora',
            'calculadora:perfil',
            'calculadora:api_registro',
            'calculadora:api_login',
            'calculadora:api_logout',
            'calculadora:api_perfil',
            'calculadora:api_deletar_conta',
            'calculadora:api_calcular',
            'calculadora:api_operacoes',
            'calculadora:api_limpar_historico',
            'calculadora:api_estatisticas',
        ]
        
        for url_name in urls_to_test:
            with self.subTest(url=url_name):
                url = reverse(url_name)
                self.assertIsNotNone(url)
                
    def test_url_com_parametro(self):
        """Testa URL que aceita parâmetros."""
        url = reverse('calculadora:api_usuario_update', kwargs={'pk': 1})
        self.assertIsNotNone(url)
        self.assertIn('/1/', url)