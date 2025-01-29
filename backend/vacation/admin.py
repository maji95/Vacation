from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, Department, User, RegistrationQueue, VacationRequest

# Register your models here.

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)
    search_fields = ('role_name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('full_name', 'telegram_id', 'department', 'role', 'vacation_days', 
                   'is_manager', 'is_hr', 'is_director', 'is_admin', 'is_staff', 'is_active')
    list_filter = ('department', 'role', 'is_manager', 'is_hr', 'is_director', 'is_admin', 'is_staff', 'is_active')
    search_fields = ('full_name', 'telegram_id')
    ordering = ('full_name',)
    
    fieldsets = (
        (None, {'fields': ('telegram_id', 'password')}),
        ('Personal info', {'fields': ('full_name', 'department', 'role', 'vacation_days')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                  'is_manager', 'is_hr', 'is_director', 'is_admin')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telegram_id', 'full_name', 'password1', 'password2'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.password:  # Если это новый пользователь и пароль не установлен
            obj.set_unusable_password()
        super().save_model(request, obj, form, change)

@admin.register(RegistrationQueue)
class RegistrationQueueAdmin(admin.ModelAdmin):
    list_display = ('entered_name', 'telegram_id', 'created_at')
    search_fields = ('entered_name', 'telegram_id')
    ordering = ('-created_at',)

@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__full_name', 'comments')
    ordering = ('-created_at',)
