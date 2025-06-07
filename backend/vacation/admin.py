from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Department, User, RegistrationQueue, VacationRequest, NameDictionary, ApprovalFirst, ApprovalSecond, ApprovalFinal, ApprovalDone, ApprovalProcess

# Register your models here.

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('full_name', 'telegram_id', 'vacation_days', 'is_active')
    list_filter = ('is_active', 'is_hr', 'is_director', 'is_admin')
    search_fields = ('full_name', 'telegram_id')
    ordering = ('full_name',)
    
    fieldsets = (
        (None, {'fields': ('telegram_id', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                  'is_hr', 'is_director', 'is_admin')}),
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
    list_filter = ('status', 'created_at')
    search_fields = ('user__full_name', 'comments')
    ordering = ('-created_at',)

@admin.register(NameDictionary)
class NameDictionaryAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'latin_name', 'department')
    search_fields = ('original_name', 'latin_name', 'department')
    ordering = ('original_name',)

@admin.register(ApprovalFirst)
class ApprovalFirstAdmin(admin.ModelAdmin):
    list_display = ('vacation_request', 'name', 'name_approval', 'status', 'date', 'comment')
    list_filter = ('status', 'date')
    search_fields = ('name', 'name_approval')
    ordering = ('-date',)

@admin.register(ApprovalSecond)
class ApprovalSecondAdmin(admin.ModelAdmin):
    list_display = ('vacation_request', 'name', 'name_approval', 'status', 'date', 'comment')
    list_filter = ('status', 'date')
    search_fields = ('name', 'name_approval')
    ordering = ('-date',)

@admin.register(ApprovalFinal)
class ApprovalFinalAdmin(admin.ModelAdmin):
    list_display = ('vacation_request', 'name', 'name_approval', 'status', 'date', 'comment')
    list_filter = ('status', 'date')
    search_fields = ('name', 'name_approval')
    ordering = ('-date',)

@admin.register(ApprovalDone)
class ApprovalDoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_approval', 'status', 'date')
    list_filter = ('status', 'date')
    search_fields = ('name', 'name_approval')
    ordering = ('-date',)

@admin.register(ApprovalProcess)
class ApprovalProcessAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'first_approval', 'second_approval', 'final_approval', 'replacement', 'timekeeper')
    search_fields = ('original_name', 'employee_name', 'first_approval', 'second_approval', 'final_approval')
    ordering = ('employee_name',)
