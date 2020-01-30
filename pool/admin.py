from django.contrib import admin
from pool.models import NewsItem, Team, Season, Week, WeekType, Fee, Rule, Game, Alert, Winner, Talk, PickType, CustomUser, PayerAudit, Pick, PayerAudit, City, Preferences, Stadium
from django.db import models
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm, GameForm, AlertForm, ScoresForm, PayerAuditForm, PickForm, TalkAdminForm, WinnerForm, PickAdminForm, PickTypeAdminForm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['username', 'first_name', 'last_name', 'email', 'favorite_team']
    search_fields = ['username', 'last_name', 'email']
    empty_value_display = '-empty-'

class PayerAuditAdmin(admin.ModelAdmin):
    model = PayerAudit
    form = PayerAuditForm
    list_display = ['user', 'has_paid', 'payment_method', 'date_sent', 'date_received']
    ordering = ['-user__username']
    list_filter = ('has_paid', 'payment_method',)
    list_per_page = 16
    search_fields = ['user']
    fields = (('user', 'has_paid'), 'payment_method', ('date_sent', 'date_received'),)

    # def has_delete_permission(self, request, obj=None):
    #     return False

class NewsItemAdmin(admin.ModelAdmin):
    model = NewsItem
    list_display = ['message', 'effective_date', 'effective_end_date']
    ordering = ['effective_date', 'effective_end_date']

class TeamAdmin(admin.ModelAdmin):
    model = Team
    fields = (('name', 'abbreviation'), ('nick_name', 'short_nick_name'), 'division', ('image_name', 'small_image_name'), ('color_01','color_02','color_03','color_04'))
    list_display = ('name', 'nick_name', 'team_colors', 'image_name', 'division',)
    list_filter = ('division', 'division__conference',)
    list_per_page = 16
    search_fields = ['name']
        
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class SeasonAdmin(admin.ModelAdmin):
    model = Season
    list_display = ['name', 'effective_date', 'effective_end_date', 'is_active']
    ordering = ['-effective_date']

class TeamInline(admin.TabularInline):
    model = Team
    readonly_fields = ('home_team', 'visiting_team',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request):
        return False

class GameInline(admin.TabularInline):
    model = Game
    form = GameForm
    extra = 1    

class WeekAdmin(admin.ModelAdmin):
    model = Week
    fields = (('name', 'effective_date', 'effective_end_date', 'is_active'), ('week_type', 'season'))
    list_display = ['week_type', 'name', 'effective_date', 'effective_end_date', 'is_active']
    ordering = ['id']
    list_filter = ('week_type__name', )
    inlines = [GameInline]        

class FeeAdmin(admin.ModelAdmin):
    model = Fee
    list_display = ['amount', 'country', 'label_for_local_amount', 'exchange_source', 'exchange_rate_date']
    fields = ('amount', ('country', 'local_amount'), ('exchange_source', 'exchange_rate_date'))

class PickInline(admin.TabularInline):
    model = Pick
    form = PickAdminForm
    extra = 0
    ordering = ['-score', 'user']

    readonly_fields = ('user', 'pick_type', 'score', 'last_saved_date')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class GameAdmin(admin.ModelAdmin):
    model = Game
    form = ScoresForm
    ordering = ['week__effective_date', 'number']
    list_per_page = 16
    list_filter = ('week__week_type', 'week')
    list_display = ('game_no', 'start_time', 'game_with_results',)
    date_hierarchy = 'week__effective_date'
    fields = (('number', 'start_time', 'game_status', 'city'), ('home_team', 'home_score'), ('visiting_team', 'visitor_score', 'is_regulation_tie'), )
    inlines = [PickInline]

    def has_add_permission(self, request):
        return False

class AlertAdmin(admin.ModelAdmin):
    model = Alert
    form = AlertForm
    fields = (('user', 'alert_level'), ('effective_date', 'effective_end_date'), 'message')
    list_display = ['user', 'effective_date', 'effective_end_date']
    list_per_page = 16
    list_filter = ('user__username', 'user__last_name',)
    
class RulesAdmin(admin.ModelAdmin):
    model = Rule
    list_display = ['title', 'points', 'message']
    
class WinnersAdmin(admin.ModelAdmin):
    model = Winner
    form = WinnerForm
    list_display = ['week', 'user', 'message']
    list_filter = ('week__week_type', )
    ordering = ['id']

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False
    
class TalkAdmin(admin.ModelAdmin):
    model = Talk
    form = TalkAdminForm
    list_per_page = 16
    list_display = ['user', 'message', 'effective_date', 'effective_end_date']
    list_filter = ('user__username',)
    fields = ('user', 'message', ('effective_date', 'effective_end_date'),)

class PickAdmin(admin.ModelAdmin):
    model = Pick
    form = PickForm
    list_per_page = 16
    list_display = ['user', 'game', 'score', 'pick_type']
    list_filter = ('user__username', 'game__week', )
    ordering = ['game__number']

class PickTypeAdmin(admin.ModelAdmin):
    model = PickType
    form = PickTypeAdminForm
    list_display = ['name', 'value', 'is_active', 'description']
    readonly_fields = ('name', 'value')
    fields = ('name', 'value', 'is_active', 'description')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class WeekTypeAdmin(admin.ModelAdmin):
    model = WeekType
    list_display = ['name', 'is_active']
    readonly_fields = ('name',)
    fields = ('name', 'is_active',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class CityAdmin(admin.ModelAdmin):
    model = City
    list_display = ['name', 'stadium', 'country']
    ordering = ['name']

class StadiumAdmin(admin.ModelAdmin):
    model = City
    list_display = ['name', 'capacity', 'surface']
    ordering = ['name']

class PreferencesAdmin(admin.ModelAdmin):
    model = Preferences
    list_display = ['user', 'picks_page_layout_type']
    ordering = ['user']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PayerAudit, PayerAuditAdmin)    
admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(PickType, PickTypeAdmin)
admin.site.register(WeekType, WeekTypeAdmin)
admin.site.register(Fee, FeeAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Rule, RulesAdmin)
admin.site.register(Winner, WinnersAdmin)
admin.site.register(Talk, TalkAdmin)
admin.site.register(Pick, PickAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Preferences, PreferencesAdmin)
admin.site.register(Stadium, StadiumAdmin)
# admin.site.register(PageLayoutType)

