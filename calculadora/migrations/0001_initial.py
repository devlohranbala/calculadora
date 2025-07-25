# Generated by Django 5.0.1 on 2025-07-24 02:39

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('nome', models.CharField(max_length=150, verbose_name='Nome completo')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última atualização')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Usuário',
                'verbose_name_plural': 'Usuários',
                'db_table': 'usuarios',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Operacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operacao', models.TextField(verbose_name='Expressão matemática')),
                ('resultado', models.CharField(max_length=255, verbose_name='Resultado')),
                ('tipo_operacao', models.CharField(choices=[('+', 'Soma'), ('-', 'Subtração'), ('*', 'Multiplicação'), ('/', 'Divisão'), ('mixed', 'Operação Mista')], default='mixed', max_length=10, verbose_name='Tipo de operação')),
                ('data_inclusao', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data da operação')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operacoes', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Operação',
                'verbose_name_plural': 'Operações',
                'db_table': 'operacoes',
                'ordering': ['-data_inclusao'],
                'indexes': [models.Index(fields=['usuario', '-data_inclusao'], name='operacoes_usuario_c22b89_idx'), models.Index(fields=['tipo_operacao'], name='operacoes_tipo_op_226fba_idx')],
            },
        ),
    ]
