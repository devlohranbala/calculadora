from django.urls import path
from . import views

app_name = 'calculadora'

urlpatterns = [
    # URLs para servir templates HTML
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('calculadora/', views.calculadora_view, name='calculadora'),
    path('perfil/', views.perfil_view, name='perfil'),
    
    # APIs de autenticação
    path('api/auth/register/', views.RegistroAPIView.as_view(), name='api_registro'),
    path('api/auth/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/auth/logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/auth/profile/', views.PerfilAPIView.as_view(), name='api_perfil'),
    path('api/auth/deletar-conta/', views.DeletarContaAPIView.as_view(), name='api_deletar_conta'),
    path('api/usuarios/<int:pk>/', views.PerfilAPIView.as_view(), name='api_usuario_update'),
    
    # APIs de operações matemáticas
    path('api/operacoes/calcular/', views.CalcularAPIView.as_view(), name='api_calcular'),
    path('api/operacoes/', views.OperacoesListAPIView.as_view(), name='api_operacoes'),
    path('api/operacoes/limpar_historico/', views.LimparHistoricoAPIView.as_view(), name='api_limpar_historico'),
    path('api/estatisticas/', views.EstatisticasAPIView.as_view(), name='api_estatisticas'),
]