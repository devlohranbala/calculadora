import re
from typing import Any, Dict
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Usuario, Operacao
from .serializers import (
    UsuarioSerializer, 
    UsuarioRegistroSerializer, 
    LoginSerializer,
    OperacaoSerializer, 
    CalcularSerializer
)


def login_view(request: HttpRequest) -> HttpResponse:
    """View para servir a página de login."""
    return render(request, 'login.html')


def calculadora_view(request: HttpRequest) -> HttpResponse:
    """View para servir a página da calculadora."""
    return render(request, 'calculadora.html')


def perfil_view(request: HttpRequest) -> HttpResponse:
    """View para servir a página de perfil."""
    return render(request, 'perfil.html')
class RegistroAPIView(APIView):
    """API para registro de novos usuários."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request: HttpRequest) -> Response:
        try:
            serializer = UsuarioRegistroSerializer(data=request.data)
            
            if serializer.is_valid():
                usuario = serializer.save()
                

                login(request, usuario)
                
                return Response({
                    'message': 'Usuário criado com sucesso!',
                    'user': UsuarioSerializer(usuario).data,
                    'authenticated': True
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Dados inválidos',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': 'Erro interno do servidor',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPIView(APIView):
    """API para autenticação de usuários."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request: HttpRequest) -> Response:
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            

            login(request, usuario)
            
            return Response({
                'message': 'Login realizado com sucesso!',
                'usuario': UsuarioSerializer(usuario).data,
                'authenticated': True
            }, status=status.HTTP_200_OK)
        
        return Response({
            'erro': 'Credenciais inválidas',
            'detalhes': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    """API para logout de usuários."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: HttpRequest) -> Response:
        logout(request)
        return Response({
            'message': 'Logout realizado com sucesso!',
            'authenticated': False
        }, status=status.HTTP_200_OK)


class PerfilAPIView(generics.RetrieveUpdateAPIView):
    """API para visualizar e atualizar perfil do usuário."""
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self) -> Usuario:
        return self.request.user



class CalcularAPIView(APIView):
    """API para realizar cálculos matemáticos."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: HttpRequest) -> Response:
        serializer = CalcularSerializer(data=request.data)
        
        if serializer.is_valid():
            operacao_str = serializer.validated_data['operacao']
            
            try:

                resultado = self._calcular_seguro(operacao_str)
                

                operacao = Operacao.objects.create(
                    usuario=request.user,
                    operacao=operacao_str,
                    resultado=str(resultado)
                )
                
                return Response({
                    'operacao': operacao_str,
                    'resultado': resultado,
                    'id': operacao.id,
                    'data_inclusao': operacao.data_inclusao
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'erro': 'Erro no cálculo',
                    'detalhes': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'erro': 'Dados inválidos',
            'detalhes': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _calcular_seguro(self, operacao: str) -> float:
        """Calcula uma expressão matemática de forma segura."""

        operacao = operacao.replace(' ', '')
        

        if not re.match(r'^[0-9+\-*/().]+$', operacao):
            raise ValueError('Operação contém caracteres não permitidos')
        

        if operacao.count('(') != operacao.count(')'):
            raise ValueError('Parênteses não balanceados')
        

        if '/0' in operacao.replace(' ', ''):
            raise ValueError('Divisão por zero não é permitida')
        
        try:

            resultado = eval(operacao, {"__builtins__": {}}, {})
            

            if not isinstance(resultado, (int, float)):
                raise ValueError('Resultado inválido')
            

            if isinstance(resultado, float):
                resultado = round(resultado, 10)
            
            return resultado
            
        except ZeroDivisionError:
            raise ValueError('Divisão por zero não é permitida')
        except (SyntaxError, NameError, TypeError):
            raise ValueError('Expressão matemática inválida')
        except OverflowError:
            raise ValueError('Resultado muito grande')


class OperacoesListAPIView(generics.ListAPIView):
    """API para listar operações do usuário."""
    serializer_class = OperacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Operacao.objects.filter(usuario=self.request.user)


class LimparHistoricoAPIView(APIView):
    """API para limpar histórico de operações do usuário."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: HttpRequest) -> Response:
        operacoes_deletadas = Operacao.objects.filter(usuario=request.user).count()
        Operacao.objects.filter(usuario=request.user).delete()
        
        return Response({
            'message': 'Histórico limpo com sucesso!',
            'operacoes_deletadas': operacoes_deletadas
        }, status=status.HTTP_200_OK)


class EstatisticasAPIView(APIView):
    """API para obter estatísticas do usuário."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: HttpRequest) -> Response:
        usuario = request.user
        hoje = timezone.now().date()
        semana_passada = hoje - timedelta(days=7)
        

        total_operacoes = Operacao.objects.filter(usuario=usuario).count()
        operacoes_hoje = Operacao.objects.filter(
            usuario=usuario,
            data_inclusao__date=hoje
        ).count()
        operacoes_semana = Operacao.objects.filter(
            usuario=usuario,
            data_inclusao__date__gte=semana_passada
        ).count()
        

        operacoes_por_tipo = Operacao.objects.filter(usuario=usuario).values(
            'tipo_operacao'
        ).annotate(count=Count('id'))
        
        return Response({
            'total_operacoes': total_operacoes,
            'operacoes_hoje': operacoes_hoje,
            'operacoes_semana': operacoes_semana,
            'operacoes_por_tipo': list(operacoes_por_tipo),
            'membro_desde': usuario.data_cadastro.strftime('%B %Y')
        }, status=status.HTTP_200_OK)


class DeletarContaAPIView(APIView):
    """API para deletar conta do usuário."""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request: HttpRequest) -> Response:
        usuario = request.user
        
        try:

            Operacao.objects.filter(usuario=usuario).delete()
            

            logout(request)
            

            usuario.delete()
            
            return Response({
                'message': 'Conta deletada com sucesso!',
                'authenticated': False
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'erro': 'Erro ao deletar conta',
                'detalhes': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
