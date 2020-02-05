# from django.http import request
from django.utils import timezone

def get_now():
    return timezone.now()

def has_start_time_passed(start_time):
    now = get_now() 
    return start_time < now

def is_game_not_yet_started(start_time):
    now = get_now()
    return start_time > now

def is_underway(start_time, is_over):
    
    if start_time < get_now():
        return is_over
    else:
        return False
