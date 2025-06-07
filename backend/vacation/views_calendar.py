from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import VacationRequest
from datetime import datetime
import calendar

# --- Календарь отпусков ---

@login_required
def calendar_view(request):
    """
    Страница календаря отпусков
    """
    # ... (реализация переносится из views.py)
    pass
