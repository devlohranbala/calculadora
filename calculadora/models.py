from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):
    """Modelo customizado de usuário para a calculadora."""
    nome = models.CharField(max_length=150, verbose_name="Nome completo")
    email = models.EmailField(unique=True, verbose_name="Email")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'username']
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        db_table = "usuarios"
    
    def __str__(self) -> str:
        return f"{self.nome} ({self.email})"
    
    def save(self, *args, **kwargs) -> None:
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class Operacao(models.Model):
    """Modelo para armazenar operações matemáticas dos usuários."""
    TIPOS_OPERACAO = [
        ('+', 'Soma'),
        ('-', 'Subtração'),
        ('*', 'Multiplicação'),
        ('/', 'Divisão'),
        ('mixed', 'Operação Mista'),
    ]
    
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='operacoes',
        verbose_name="Usuário"
    )
    operacao = models.TextField(verbose_name="Expressão matemática")
    resultado = models.CharField(max_length=255, verbose_name="Resultado")
    tipo_operacao = models.CharField(
        max_length=10, 
        choices=TIPOS_OPERACAO, 
        default='mixed',
        verbose_name="Tipo de operação"
    )
    data_inclusao = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Data da operação"
    )
    
    class Meta:
        verbose_name = "Operação"
        verbose_name_plural = "Operações"
        db_table = "operacoes"
        ordering = ['-data_inclusao']
        indexes = [
            models.Index(fields=['usuario', '-data_inclusao']),
            models.Index(fields=['tipo_operacao']),
        ]
    
    def __str__(self) -> str:
        return f"{self.operacao} = {self.resultado} ({self.usuario.nome})"
    
    def save(self, *args, **kwargs) -> None:
        if not self.tipo_operacao or self.tipo_operacao == 'mixed':
            self.tipo_operacao = self._detectar_tipo_operacao()
        super().save(*args, **kwargs)
    
    def _detectar_tipo_operacao(self) -> str:
        """Detecta o tipo de operação baseado na expressão matemática."""
        operacao_limpa = self.operacao.replace(' ', '')
        

        operadores = {'+': 0, '-': 0, '*': 0, '/': 0}
        for char in operacao_limpa:
            if char in operadores:
                operadores[char] += 1
        

        operadores_usados = [op for op, count in operadores.items() if count > 0]
        
        if len(operadores_usados) == 1:
            return operadores_usados[0]
        
        return 'mixed'
