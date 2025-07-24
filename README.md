# 🧮 Calculadora Web - Django

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descrição

Calculadora web moderna desenvolvida com Django, seguindo o padrão MVC. Inclui sistema de autenticação, operações matemáticas, histórico de cálculos e API REST completa.

## Funcionalidades

### 🔐 Autenticação
- Sistema de registro e login de usuários
- Autenticação básica do Django com sessões
- Proteção de rotas com middleware de autenticação
- Gerenciamento de perfil do usuário

### 🧮 Calculadora
- Operações matemáticas básicas: soma, subtração, multiplicação, divisão
- Interface web moderna e responsiva
- Suporte a expressões matemáticas complexas
- Validação de entrada e tratamento de erros

### 📊 Histórico
- Armazenamento de todas as operações realizadas
- Visualização do histórico por usuário
- Paginação de resultados
- Funcionalidade para limpar histórico
- Estatísticas de uso (operações hoje, esta semana, total)

### 🎨 Interface
- Design moderno com gradientes e efeitos visuais
- Responsivo para dispositivos móveis
- Tema escuro com cores vibrantes
- Animações e transições suaves

## Estrutura do Projeto

```
calculadora/
├── kogui_calculator/          # Projeto Django principal
│   ├── settings.py           # Configurações do Django
│   ├── urls.py              # URLs principais
│   └── wsgi.py              # Configuração WSGI
├── calculadora/              # App principal
│   ├── models.py            # Modelos (Usuario, Operacao)
│   ├── views.py             # Views da API REST
│   ├── serializers.py       # Serializers do DRF
│   ├── urls.py              # URLs do app
│   ├── admin.py             # Configuração do admin
│   ├── templates/           # Templates HTML
│   │   ├── login.html       # Página de login/registro
│   │   ├── calculadora.html # Página da calculadora
│   │   └── perfil.html      # Página de perfil
│   └── static/              # Arquivos estáticos
│       └── kogui_tech_logo.jpeg
├── venv/                     # Ambiente virtual Python
└── db.sqlite3               # Banco de dados SQLite
```

## Tecnologias Utilizadas

### Backend
- **Python 3.13** - Linguagem de programação
- **Django 5.0.1** - Framework web
- **Django REST Framework** - API REST
- **Django REST Framework** - API REST com autenticação de sessão
- **Django CORS Headers** - Configuração CORS
- **SQLite** - Banco de dados

### Frontend
- **HTML5** - Estrutura das páginas
- **CSS3** - Estilização moderna
- **JavaScript ES6+** - Interatividade
- **Fetch API** - Comunicação com backend

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/calculadora-django.git
   cd calculadora-django
   ```

2. **Crie e ative um ambiente virtual**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute as migrações**
   ```bash
   python manage.py migrate
   ```

5. **Crie um superusuário (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Inicie o servidor**
   ```bash
   python manage.py runserver
   ```

7. **Acesse a aplicação**
   - Navegue para: http://127.0.0.1:8000/

## Como Usar

### 1. Registro/Login
- Acesse a página inicial (http://127.0.0.1:8000/)
- Clique em "Não tem conta? Criar uma" para se registrar
- Ou faça login com suas credenciais existentes

### 2. Calculadora
- Após o login, você será redirecionado para a calculadora
- Use os botões ou o teclado para inserir operações
- Pressione "=" ou Enter para calcular
- O resultado aparecerá no display e será salvo no histórico

### 3. Histórico
- Visualize todas as suas operações no painel lateral
- Use o botão "Limpar Histórico" para remover todas as operações

### 4. Perfil
- Clique em "📊 Perfil" para ver suas estatísticas
- Edite seu nome ou email clicando nos campos
- Visualize estatísticas de uso detalhadas

## API Endpoints

### Autenticação
- `POST /api/auth/register/` - Registro de usuário
- `POST /api/auth/login/` - Login de usuário
- `GET /api/auth/profile/` - Obter perfil do usuário
- `PATCH /api/usuarios/{id}/` - Atualizar perfil

### Operações
- `POST /api/operacoes/calcular/` - Realizar cálculo
- `GET /api/operacoes/` - Listar operações do usuário
- `POST /api/operacoes/limpar_historico/` - Limpar histórico
- `GET /api/estatisticas/` - Obter estatísticas

## Modelos de Dados

### Usuario
- Herda de `AbstractUser` do Django
- Campos: nome, email (único), data_cadastro, data_atualizacao
- Autenticação por email

### Operacao
- Campos: usuario (FK), operacao, resultado, tipo_operacao, data_inclusao
- Detecção automática do tipo de operação
- Ordenação por data de inclusão

## Segurança

- **Autenticação de sessão** do Django
- **Validação de entrada** para operações matemáticas
- **Proteção contra eval malicioso** com whitelist de caracteres
- **CORS configurado** para desenvolvimento
- **Validação de dados** com serializers do DRF

## Recursos Avançados

- **Cálculo seguro** com validação de expressões
- **Detecção automática** do tipo de operação
- **Paginação** do histórico
- **Estatísticas** de uso em tempo real
- **Interface responsiva** para mobile
- **Suporte a teclado** na calculadora

## 🔧 Admin Django

- Acesse: http://127.0.0.1:8000/admin/
- Use o superusuário criado durante a instalação
- Gerencie usuários e operações através da interface administrativa

## 💻 Desenvolvimento

O projeto segue as melhores práticas do Django:
- Separação clara entre Models, Views e Templates
- Uso de serializers para validação de dados
- Configuração adequada de CORS e autenticação
- Estrutura modular e escalável
- Código limpo e bem documentado

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.