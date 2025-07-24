from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Operacao


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin para o modelo Usuario."""
    list_display = ('email', 'nome', 'is_active', 'is_staff', 'data_cadastro')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'data_cadastro')
    search_fields = ('email', 'nome')
    ordering = ('-data_cadastro',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'first_name', 'last_name')}),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'data_cadastro')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('data_cadastro', 'data_atualizacao')


@admin.register(Operacao)
class OperacaoAdmin(admin.ModelAdmin):
    """Admin para o modelo Operacao."""
    list_display = ('usuario', 'operacao', 'resultado', 'tipo_operacao', 'data_inclusao')
    list_filter = ('tipo_operacao', 'data_inclusao')
    search_fields = ('usuario__email', 'usuario__nome', 'operacao')
    ordering = ('-data_inclusao',)
    readonly_fields = ('data_inclusao',)
    
    fieldsets = (
        (None, {
            'fields': ('usuario', 'operacao', 'resultado', 'tipo_operacao')
        }),
        ('Metadados', {
            'fields': ('data_inclusao',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Otimizar consultas com select_related."""
        return super().get_queryset(request).select_related('usuario')