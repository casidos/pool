import pytz
from django.utils import timezone
from django.db import models
from django.db import transaction, IntegrityError
from django.shortcuts import redirect, render
from datetime import date
import datetime
from pool.models import Week, Season
from django.shortcuts import get_object_or_404
from utils.season_helper import get_now


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)

class CurrentWeekMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        #CHECK THE CURRENT DATE TIME AGAINST WHAT WEEK SHOULD BE ACTIVE
        now = get_now()

        # if not 'selected_week_type_id'in request.session:
        #     request.session['selected_week_type_id'] = 2
        #     request.session['selected_week_id'] = 1

        # if not 'selected_week_id' in request.session:
        #     request.session['selected_week_type_id'] = 2
        #     request.session['selected_week_id'] = 1

        if 'current_season_id' in request.session:

            current_season_id = request.session['current_season_id']

            if Season.objects.filter(is_active=True).exists():
                
                # s = Season.objects.get(effective_date__lte=now, effective_end_date__gte=now)
                s = Season.objects.get(is_active=True)
                # s.is_active = True
                # s.save()
                if not s.id == current_season_id:
                  current_season_id = s.id  
            else:
                current_season_id = 0
        else:
            current_season_id = 0
            
        if 'current_week_id' in request.session:

            current_week_id = request.session['current_week_id']

            if Week.objects.filter(is_active=True).exists():
                w = Week.objects.get(effective_date__lte=now, effective_end_date__gte=now)
                # w.is_active = True
                # w.save()

                if not w.id == current_week_id:
                    current_week_id = w.id  
            else:
                current_week_id = 0                
        else:
            current_week_id = 0
        
        request.session['current_season_id'] = current_season_id       
        request.session['current_week_id'] = current_week_id 

        return self.get_response(request)


    