from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, Operacao


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Usuario."""
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'data_cadastro', 'data_atualizacao']
        read_only_fields = ['id', 'data_cadastro', 'data_atualizacao']


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de novos usuários."""
    senha = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        error_messages={
            'required': 'A senha é obrigatória.',
            'min_length': 'A senha deve ter pelo menos 8 caracteres.',
            'blank': 'A senha não pode estar vazia.'
        }
    )
    confirmar_senha = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
        error_messages={
            'blank': 'A confirmação de senha não pode estar vazia.'
        }
    )
    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha', 'confirmar_senha']
        extra_kwargs = {
            'email': {
                'error_messages': {
                    'required': 'O email é obrigatório.',
                    'invalid': 'Digite um email válido.',
                    'blank': 'O email não pode estar vazio.'
                }
            }
        }
    
    def validate_nome(self, value: str) -> str:
        """Validar nome do usuário."""
        if not value or not value.strip():
            raise serializers.ValidationError('O nome não pode estar vazio.')
        
        value = value.strip()
        
        if len(value) < 2:
            raise serializers.ValidationError('O nome deve ter pelo menos 2 caracteres.')
        
        if len(value) > 150:
            raise serializers.ValidationError('O nome não pode ter mais de 150 caracteres.')
        

        import re
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'\-\.]+$', value):
            raise serializers.ValidationError('O nome deve conter apenas letras, espaços e caracteres válidos.')
        
        return value
    
    def validate_email(self, value: str) -> str:
        """Validar email do usuário."""
        if not value or not value.strip():
            raise serializers.ValidationError('O email não pode estar vazio.')
        
        value = value.strip().lower()
        

        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError('Digite um email válido. Exemplo: usuario@exemplo.com')
        

        dominios_bloqueados = ['10minutemail.com', 'tempmail.org', 'guerrillamail.com']
        dominio = value.split('@')[1]
        if dominio in dominios_bloqueados:
            raise serializers.ValidationError('Este provedor de email não é permitido.')
        
        return value
    
    def validate(self, attrs: dict) -> dict:
        """Validação customizada para registro de usuário."""

        confirmar_senha = attrs.get('confirmar_senha')
        if confirmar_senha and attrs['senha'] != confirmar_senha:
            raise serializers.ValidationError({
                'confirmar_senha': 'As senhas não coincidem.'
            })
        

        try:
            validate_password(attrs['senha'])
        except Exception as e:
            raise serializers.ValidationError({
                'senha': list(e.messages) if hasattr(e, 'messages') else ['A senha não atende aos critérios de segurança.']
            })
        

        if Usuario.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': 'Este email já está cadastrado. Tente fazer login ou use outro email.'
            })
        
        return attrs
    
    def create(self, validated_data: dict) -> Usuario:
        """Criar novo usuário com senha criptografada."""
        validated_data.pop('confirmar_senha', None)
        senha = validated_data.pop('senha')
        
        usuario = Usuario.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            nome=validated_data['nome'],
            password=senha
        )
        
        return usuario


class LoginSerializer(serializers.Serializer):
    """Serializer para autenticação de usuários."""
    email = serializers.EmailField(
        error_messages={
            'required': 'O email é obrigatório.',
            'invalid': 'Digite um email válido.',
            'blank': 'O email não pode estar vazio.'
        }
    )
    senha = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        error_messages={
            'required': 'A senha é obrigatória.',
            'blank': 'A senha não pode estar vazia.'
        }
    )
    
    def validate_email(self, value: str) -> str:
        """Validar formato do email."""
        if not value or not value.strip():
            raise serializers.ValidationError('O email não pode estar vazio.')
        
        value = value.strip().lower()
        

        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError('Digite um email válido.')
        
        return value
    
    def validate_senha(self, value: str) -> str:
        """Validar senha."""
        if not value:
            raise serializers.ValidationError('A senha não pode estar vazia.')
        
        if len(value) < 1:
            raise serializers.ValidationError('A senha é obrigatória.')
        
        return value
    
    def validate(self, attrs: dict) -> dict:
        """Validar credenciais do usuário."""
        email = attrs.get('email')
        senha = attrs.get('senha')
        
        if not email or not senha:
            raise serializers.ValidationError({
                'non_field_errors': ['Email e senha são obrigatórios.']
            })
        

        try:
            usuario_existe = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({
                'email': ['Este email não está cadastrado. Verifique o email ou crie uma conta.']
            })
        

        usuario = authenticate(
            request=self.context.get('request'),
            username=email,
            password=senha
        )
        
        if not usuario:

            raise serializers.ValidationError({
                'senha': ['Senha incorreta. Verifique sua senha e tente novamente.']
            })
        
        if not usuario.is_active:
            raise serializers.ValidationError({
                'non_field_errors': ['Sua conta foi desativada. Entre em contato com o suporte.']
            })
        
        attrs['usuario'] = usuario
        return attrs


class OperacaoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Operacao."""
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    
    class Meta:
        model = Operacao
        fields = [
            'id', 'operacao', 'resultado', 'tipo_operacao', 
            'data_inclusao', 'usuario', 'usuario_nome'
        ]
        read_only_fields = ['id', 'data_inclusao', 'usuario', 'usuario_nome']
    
    def create(self, validated_data: dict) -> Operacao:
        """Criar nova operação associada ao usuário autenticado."""
        request = self.context.get('request')
        validated_data['usuario'] = request.user
        return super().create(validated_data)


class CalcularSerializer(serializers.Serializer):
    """Serializer para processar cálculos matemáticos."""
    operacao = serializers.CharField(
        max_length=500,
        help_text="Expressão matemática para calcular (ex: 2+2, 10*5-3)"
    )
    
    def validate_operacao(self, value: str) -> str:
        """Validar se a operação contém apenas caracteres permitidos."""
        import re
        
        if not value or not value.strip():
            raise serializers.ValidationError('A operação não pode estar vazia.')
        
        value = value.strip()
        
        if len(value) > 500:
            raise serializers.ValidationError('A operação é muito longa. Máximo de 500 caracteres.')
        
        padrao_permitido = re.compile(r'^[0-9+\-*/().\s]+$')
        
        if not padrao_permitido.match(value):
            raise serializers.ValidationError(
                'A operação contém caracteres não permitidos. '
                'Use apenas números e operadores básicos (+, -, *, /, parênteses).'
            )
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError('A operação deve conter pelo menos um número.')
        
        if not re.search(r'[+\-*/]', value):
            raise serializers.ValidationError('A operação deve conter pelo menos um operador (+, -, *, /).')
        
        if value.count('(') != value.count(')'):
            raise serializers.ValidationError('Os parênteses não estão balanceados.')
        
        if '/0' in value.replace(' ', '') or '/ 0' in value:
            raise serializers.ValidationError('Divisão por zero não é permitida.')
        
        operadores_consecutivos = re.search(r'[+*/]{2,}|--', value.replace(' ', ''))
        if operadores_consecutivos:
            raise serializers.ValidationError('Operadores consecutivos não são permitidos.')
        
        value_sem_espacos = value.replace(' ', '')
        if re.match(r'^[+*/]', value_sem_espacos) or re.search(r'[+\-*/]$', value_sem_espacos):
            raise serializers.ValidationError('A operação não pode começar ou terminar com um operador.')
        
        return value