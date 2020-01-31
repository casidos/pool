#pool/views.py
import pytz
from django.http import QueryDict
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date
import datetime
from .models import *
from .forms import CustomUserCreationForm, EditUserForm, TalkForm
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext

def get_users_no_picks(request):
    args = get_current(request)
    current_week = args.get('current_week')
    picks = Pick.objects.prefetch_related('game_id__week_id').filter(game_id__week_id = current_week.id, pick_type_id = 1)
    users = set()
    
    for p in picks:
        users.add(p.user)  

    return users

class StandingsView(LoginRequiredMixin, TemplateView):
    pass

class AdminNoPicks(LoginRequiredMixin, TemplateView):
    template_name = 'admin_no_picks.html'

    def get(self, request): 
        
        args = get_current(request)    

        users = get_users_no_picks(request)   
        # users = {}

        args.update({'template_name' : self.template_name})
        args.update({'users' : users})

        return render(request, self.template_name, args)   

class CreateUser(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'create_user.html'

    def form_valid(self, form):
        clean = form.cleaned_data   
        set_timezone(self.request)
        return super(CreateUser, self).form_valid(form)

class EditUser(LoginRequiredMixin, UpdateView):  
    
    context_object_name = 'customUser'
    form_class = EditUserForm
    template_name = 'edit_user.html'
    success_url = '/edit_user'

    def get_object(self, queryset=None): 
        return self.request.user

    def form_valid(self, form):
        clean = form.cleaned_data   
        set_timezone(self.request)
        return super(EditUser, self).form_valid(form)

class TalkView(LoginRequiredMixin, TemplateView):
    template_name = 'talk.html'
    context_object_name = 'talk'
    form_class = TalkForm
    success_url = '/talk'
    
    def get(self, request):
        current_season = Season.objects.filter(is_active=True).latest('effective_date')
        seasons = Season.objects.order_by('-effective_date')
        queryset = Talk.objects.order_by('-effective_date')
        form = TalkForm()
        args = {'form': form, 'talk' : queryset, 'current_season' : current_season, 'seasons' : seasons}
        return render(request, self.template_name, args)    

    def post(self, request):
        form = TalkForm(request.POST)
        if form.is_valid():
            talk = form.save(commit=False)
            talk.user = request.user
            talk.effective_date = datetime.datetime.now()
            talk.effective_end_date = datetime.datetime.now() + timedelta(days=21)
            talk.save()
        
        form = TalkForm()
        queryset = Talk.objects.order_by('-effective_date')
        args = {'form': form, 'talk' : queryset}
        return render(request, self.template_name, args)    

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            return redirect('/users/login')

    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'change_password.html', args)

def set_timezone(request):

    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
    else:
        return render(request, 'home.html', {'timezones': pytz.common_timezones})

class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    
    def get(self, request): 
        
        #HAS TO EXIST OR WE WOULDN'T BE HERE
        args = get_current(request)       

        args.update({'template_name' : self.template_name})
        args.update({'news_items' : NewsItem.objects.order_by('-effective_date')[:3]})
        args.update({'alerts' : Alert.objects.filter(user_id=request.user.id)})
        args.update({'the_time' : get_now()})

        return render(request, self.template_name, args)        
    
class NewsItemsView(LoginRequiredMixin, ListView):
    template_name = 'news.html'
    
    def get(self, request):    
        
        args = get_current(request)
        now = datetime.datetime.now()
        args.update({'items' : NewsItem.objects.filter(effective_date__lte=now, effective_end_date__gte=now)})

        return render(request, self.template_name, args)

class RulesView(LoginRequiredMixin, ListView):
    template_name = 'rules.html'        

    def get(self, request):
        args = get_current(request)

        args.update({'items' : Rule.objects.all()})
        
        return render(request, self.template_name, args)

class WinnersView(LoginRequiredMixin, ListView):
    template_name = 'winners.html'
    
    def get(self, request):

        args = get_winners_args(request, 2)

        return render(request, self.template_name, args)

class FeesView(LoginRequiredMixin, ListView):
    template_name = 'fees.html'        

    def get(self, request):     
        
        args = get_current(request)

        args.update({'items' : Fee.objects.all()})

        return render(request, self.template_name, args)

@login_required
def change_layout_type_for_picks(request, pk):
    template_name = 'picks.html'
    selected_page_layout_type = PageLayoutType.objects.get(pk=pk)
    Preferences.objects.filter(user_id=request.user.id).update(picks_page_layout_type_id=selected_page_layout_type.id)
    return redirect('picks')
    
@login_required
def change_layout_type_for_winners(request, pk):
    template_name = 'winners.html'
    selected_page_layout_type = PageLayoutType.objects.get(pk=pk)
    Preferences.objects.filter(user_id=request.user.id).update(winners_page_layout_type_id=selected_page_layout_type.id)
    return redirect('winners')

@login_required
def change_selected_week_for_picks(request, pk):    
    template_name = 'picks.html'      
    args = get_picks_args(request, pk, 0)    
    return render(request, template_name, args)

@login_required
def change_week_type_for_picks(request, pk):
    template_name = 'picks.html' 
    
    args = get_picks_args(request, 0, pk)        
    
    return render(request, template_name, args)
    
@login_required
def change_week_type_for_winners(request, pk):
    template_name = 'winners.html' 
    
    args = get_winners_args(request, pk)        
    
    return render(request, template_name, args)

class PicksView(LoginRequiredMixin, ListView):
    template_name = 'picks.html'    

    def get(self, request):

        selected_week = get_selected_week(request)   

        if selected_week:
            selected_week_type = selected_week.week_type
            args = get_picks_args(request, selected_week.id, selected_week_type.id) 
        else:
            current_week = get_current_week(request)
            current_week_type = current_week.week_type
            args = get_picks_args(request, current_week.id, current_week_type.id) 
        
        return render(request, self.template_name, args) 

@login_required
def make_pick(request, pk, pt_pk):
    pick = Pick.objects.get(pk=pk)
    pick_type = PickType.objects.get(pk=pt_pk)
    pick.pick_type = pick_type
    Pick.objects.filter(id=pk).update(pick_type_id = pt_pk)
    return redirect('picks')

@login_required
def delete_alert(request, pk):
    alert = Alert.objects.get(pk=pk).delete()
    return redirect('home')

@login_required  
def delete_talk(request, pk):
    talk = Talk.objects.get(pk=pk).delete()
    return redirect('talk')

class PoolMembers(LoginRequiredMixin, ListView):
     template_name = 'pool_members.html'    

     def get(self, request): 

        args = get_current(request)

        # items = CustomUser.objects.exclude(is_superuser=True).order_by('username')
        items = CustomUser.objects.all().order_by('username')
        paginator = Paginator(items, 3) # Show 25 members per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        args.update({'items' : items})
        args.update({'page_obj' : page_obj})

        return render(request, self.template_name, args)

def get_current(request):
    current_season = None
    current_week = None
    seasons = []
    prefs = None
    
    request.session['django_timezone'] = request.user.timezone

    try:
        current_season = get_current_season(request)        
        current_week = get_current_week(request)        
        seasons = get_seasons()
        prefs = get_preferences(request)
        
    
    except Exception as e:
        print(e)
    
    return {
        'preferences' : prefs,
        'current_season': current_season,
        'current_week' : current_week,
        'seasons' : seasons
    }

def get_preferences(request):
    return Preferences.objects.get(user_id = request.user.id)

def get_seasons():
    return Season.objects.order_by('-effective_date')

def get_current_season(request):
    active_season = Season.objects.get(is_active=True)

    current_season_id = request.session['current_season_id']  

    if not active_season.id == current_season_id:
        request.session['current_season_id'] = active_season.id
        return Season.objects.get(id=active_season.id)
    else:    
        return Season.objects.get(id=current_season_id)

def get_selected_week(request):
    
    if 'selected_week_id' in request.session:
        selected_week_id = request.session['selected_week_id']  
        return Week.objects.get(id=selected_week_id)    
    else:
        return get_current_week(request)
    
def get_current_week(request):
    
    active_week = Week.objects.get(is_active=True)    
    
    current_week_id = request.session['current_week_id']  

    if not active_week.id == current_week_id:
        request.session['current_week_id'] = active_week.id
        request.session['current_week_type_id'] = active_week.week_type.id
        return Week.objects.get(id=active_week.id)
    else:
        return Week.objects.get(id=current_week_id)

def get_weeks_by_week_type(id):
    return Week.objects.filter(week_type__id = id)  

def get_winners_args(request, week_type_id):
    
    args = get_current(request)  
    
    if week_type_id == '4':
        winners = Winner.objects.all().order_by('-id')
        args.update({'winners' : winners})
        args.update({'week_types' : WeekType.objects.all().order_by('id')})
        args.update({'page_layout_types': PageLayoutType.objects.all()})

        return args
        
    week_type = WeekType.objects.get(id=week_type_id)

    if not 'selected_week_type_id' in request.session:        
        request.session['selected_week_type_id'] = week_type.id

    winners = Winner.objects.filter(week__week_type_id=week_type_id)

    args.update({'winners' : winners})
    args.update({'week_types' : WeekType.objects.filter(is_active=True).order_by('id')})
    args.update({'selected_week_type' : week_type})
    args.update({'page_layout_types': PageLayoutType.objects.all()})

    return args

def get_picks_args(request, week_id, week_type_id):

    args = get_current(request)
    
    if week_id == 0:#we are changing the week type
        selected_week_type = WeekType.objects.get(id = week_type_id)
        selected_week_type_id = selected_week_type.id
        selected_weeks = Week.objects.filter(week_type_id = selected_week_type_id)
        selected_week = selected_weeks[0]
    else:
        selected_week = Week.objects.get(id = week_id)
        request.session['selected_week_id'] = selected_week.id
        selected_week_type = selected_week.week_type
        selected_weeks = get_weeks_by_week_type(selected_week_type.id)       

    games = Game.objects.filter(week_id = selected_week.id)     

    picks = Pick.objects.prefetch_related('game_id__week_id').filter(game_id__week_id = selected_week.id, user_id = request.user.id).order_by('game__start_time')

    args.update({'picks' : picks})
    args.update({'pick_types' : PickType.objects.filter(id__gt = 3).order_by('id')})
    args.update({'selected_week' : selected_week})
    args.update({'selected_weeks' : selected_weeks})
    args.update({'page_layout_types': PageLayoutType.objects.all()})

    return args;

def send_email_reminder(request):

    emails = set()
    
    users = get_users_no_picks(request)
    args = get_current(request)
    current_week = args.get('current_week')

    for u in users:
        emails.add(u.email)
    
    messages = []

    list_of_emails = list(emails)

    for email_address in list_of_emails:
        messages.append(('Don\'t Forget to make your Picks', '%s Kick-off is almost here. Make your picks!' % (current_week.name), settings.EMAIL_HOST_USER, [email_address]))
    
    send_mass_mail((messages), fail_silently=False)

    return redirect('admin_no_picks')
