from django.db import models
from django.db import transaction, IntegrityError
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
from django.utils import timezone
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.utils.html import format_html
from django.core.exceptions import ObjectDoesNotExist
from utils.season_helper import get_now, is_game_not_yet_started, is_underway, has_start_time_passed
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

class PickType(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    value = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    description = models.TextField(max_length=250, blank=False, null=False)

    def __str__(self):
        return self.name

class AlertLevel(models.Model):
    name = models.CharField(max_length=15, blank=False, null=False)
    
    def __str__(self):
        return self.name

class GameStatus(models.Model):
    name = models.CharField(max_length=15, blank=False, null=False)

    def is_not_yet_started(self):
        return self.id == 1

    def is_underway(self):
        return self.id == 2

    def is_complete(self):
        return self.id == 3

    def __str__(self):
        return self.name

class Conference(models.Model):       
    name = models.CharField(max_length=3, blank=False, null=False)
    
    def __str__(self):
        return self.name

class Division(models.Model):
    name = models.CharField(max_length=5, blank=False, null=False)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    short_name = models.CharField('Abbr', max_length=3, blank=False, null=False)   
    
    def __str__(self):
        return '%s (%s)' % (self.name, self.short_name)
    
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

class StadiumSurface(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.name

class Stadium(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    capacity = models.PositiveIntegerField()
    surface = models.ForeignKey(StadiumSurface, on_delete=models.SET_NULL, null=True)
    year_opened = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=False)
    stadium = models.ForeignKey(Stadium, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "cities"
        order_with_respect_to = "country"

class Team(models.Model):    
    name = models.CharField(max_length=50, blank=False, null=False)
    abbreviation = models.CharField(max_length=10, blank=False, null=False)
    nick_name = models.CharField(max_length=30, blank=False, null=False)
    short_nick_name = models.CharField(max_length=10, blank=False, null=False)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=False)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=False, null=True)
    image_name = models.CharField(max_length=50, blank=False, null=False, default='NFL.gif')
    small_image_name = models.CharField(max_length=50, blank=False, null=False, default='NFL.gif')
    color_01 = models.CharField(max_length=7, blank=True, null=True)
    color_02 = models.CharField(max_length=7, blank=True, null=True)
    color_03 = models.CharField(max_length=7, blank=True, null=True)
    color_04 = models.CharField(max_length=7, blank=True, null=True)
        
    def __str__(self):
        return '%s %s' % (self.name, self.nick_name)

    def team_colors(self):
        if self.color_04 and self.color_02 == '#FFFFFF':
            return format_html('<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};color:black;border-color:black;font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>', self.color_01, self.color_01, self.color_02, self.color_02, self.color_03, self.color_03, self.color_04, self.color_04)
        elif self.color_04 and self.color_03 == '#FFFFFF':
            return format_html('<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};color:black;border-color:black;font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>', self.color_01, self.color_01, self.color_02, self.color_02, self.color_03, self.color_03, self.color_04, self.color_04)
        elif self.color_02 == '#FFFFFF':
            return format_html('<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};color:black;border-color:black;font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>', self.color_01, self.color_01, self.color_02, self.color_02, self.color_03, self.color_03)
        elif self.color_03 == '#FFFFFF':
            return format_html('<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};color:black;border-color:black;font-size:9pt;">{}</button>', self.color_01, self.color_01, self.color_02, self.color_02, self.color_03, self.color_03)
        elif self.color_04:
            return format_html('<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>', self.color_01, self.color_01, self.color_02, self.color_02, self.color_03, self.color_03, self.color_04, self.color_04)
        else:
            return format_html('<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>&#09;&#09;<button class="button" style="background-color:{};font-size:9pt;">{}</button>', self.color_01, self.color_01, self.color_02, self.color_02, self.color_03, self.color_03)

    class Meta:
        ordering = ["name"]

class MyValidator(UnicodeUsernameValidator):
    # regex = r'^[A-Za-z0-9 ]+$'
    regex = r'^[A-Za-z0-9 ]+$'
    message = _('This is not working for some reason')

class CustomUser(AbstractUser):
    US_EST = 'US/Eastern'
    TZS = [
        ('US/Alaska', 'US/Alaska'), 
        ('US/Arizona','US/Arizona'), 
        ('US/Central','US/Central'), 
        (US_EST,'US/Eastern'), 
        ('US/Hawaii','US/Hawaii'), 
        ('US/Mountain','US/Mountain'), 
        ('US/Pacific','US/Pacific'), 
        ('Europe/Amsterdam','Europe/Amsterdam'), 
        ('Europe/Athens','Europe/Athens'), 
        ('Europe/Belgrade','Europe/Belgrade'), 
        ('Europe/Berlin','Europe/Berlin'), 
        ('Europe/Brussels','Europe/Brussels'), 
        ('Europe/Bucharest','Europe/Bucharest'), 
        ('Europe/Budapest','Europe/Budapest'), 
        ('Europe/Copenhagen','Europe/Copenhagen'), 
        ('Europe/Dublin','Europe/Dublin'), 
        ('Europe/Gibraltar','Europe/Gibraltar'), 
        ('Europe/Helsinki','Europe/Helsinki'), 
        ('Europe/Istanbul','Europe/Istanbul'), 
        ('Europe/Kiev','Europe/Kiev'), 
        ('Europe/Lisbon','Europe/Lisbon'), 
        ('Europe/London','Europe/London'),
        ('Europe/Luxembourg','Europe/Luxembourg'), 
        ('Europe/Madrid','Europe/Madrid'), 
        ('Europe/Malta','Europe/Malta'), 
        ('Europe/Moscow','Europe/Moscow'), 
        ('Europe/Oslo','Europe/Oslo'), 
        ('Europe/Paris','Europe/Paris'), 
        ('Europe/Prague','Europe/Prague'), 
        ('Europe/Rome','Europe/Rome'), 
        ('Europe/Sarajevo','Europe/Sarajevo'), 
        ('Europe/Stockholm','Europe/Stockholm'), 
        ('Europe/Vienna','Europe/Vienna'), 
        ('Europe/Volgograd','Europe/Volgograd'), 
        ('Europe/Warsaw','Europe/Warsaw'), 
        ('Europe/Zurich','Europe/Zurich')
    ]

    username_validator = MyValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Names and numbers only.'),
        validators=[username_validator],
            error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    # username = models.CharField(max_length=150, unique=True, help_text='Dont be dumb', blank=False, null=False, validators=[username_validator])

    mobile = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='profile_image', blank=True, null=True)    
    # None, 'Your String For Display'
    favorite_team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=False, null=False, default=US_EST, choices=TZS)

    def get_absolute_url(self):
        return reverse('edit_user', kwargs={'pk': self.pk})

    def __str__(self):
        return self.username    

class Alert(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False, null=False)
    message = models.TextField(max_length=250, blank=False, null=False)
    effective_date = models.DateTimeField(null=True)
    effective_end_date = models.DateTimeField(null=True)
    alert_level = models.ForeignKey(AlertLevel, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return '%s : %s %s' % (self.user, self.message[:25], self.effective_date)
  
class Talk(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False, null=False)
    message = models.TextField(max_length=250, blank=False, null=False)
    effective_date = models.DateTimeField(null=True)
    effective_end_date = models.DateTimeField(null=True)

    def __str__(self):
        return '%s : %s' % (self.user, self.message[:25])

class PayerAudit(models.Model):
    ETT = 'ETT'
    ETE = 'ETE'
    POST = 'POST'
    CIP = 'CIP'
    PP = 'PP'
    OTHER = 'OTHER'
    
    PAYMENT_METHODS = [
    (ETT, 'e-Transfer Text'),
    (ETE, 'e-Transfer Email'),
    (POST, 'Canada Post'),
    (CIP, 'Cash in Person'),
    (PP, 'PayPal'),
    (OTHER, 'Other')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False, null=False)
    has_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    date_sent = models.DateField(null=True)
    date_received = models.DateField(null=True)
    message = models.TextField(max_length=250, blank=True, null=True)

    def __str__(self):
        return '%s : %s' % (self.user.username, self.has_paid)

class NewsItem(models.Model):
    title = models.CharField(max_length=30, blank=False, null=True)
    message = models.TextField(max_length=250, blank=False, null=False)
    effective_date = models.DateTimeField(null=True)
    effective_end_date = models.DateTimeField(null=True)
    
    def __str__(self):
        return '%s' % (self.message)

    class Meta:
        verbose_name_plural = "News"

class Rule(models.Model):
    title = models.CharField(max_length=30, blank=False, null=False)
    message = models.TextField(max_length=250, blank=False, null=False)   
    points = models.SmallIntegerField(default=1, null=False)

    def __str__(self):
        return '%s : %s... worth %s points' % (self.title, self.message[:25], self.points)

class Season(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    effective_date = models.DateField(blank=False, null=False)
    effective_end_date = models.DateField(blank=False, null=False)    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class WeekType(models.Model):
    
    name = models.CharField(max_length=50, blank=False, null=False)
    is_active = models.BooleanField(default=True)
        
    def __str__(self):
        return self.name

class Week(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    effective_date = models.DateField(blank=False, null=False)
    effective_end_date = models.DateField(blank=False, null=False)
    is_active = models.BooleanField(default=False)
    week_type = models.ForeignKey(WeekType, on_delete=models.CASCADE, null=False)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return '%s : %s' % (self.week_type.name, self.name)

class Winner(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    week = models.ForeignKey(Week, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField(max_length=250, blank=True, null=True)

    def __str__(self):
        return '%s : %s %s...' % (self.user, self.week, self.message)

class Game(models.Model):
    GAME_NUMBERS = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
    (9, '9'),
    (10, '10'),
    (11, '11'),
    (12, '12'),
    (13, '13'),
    (14, '14'),
    (15, '15'),
    (16, '16'),
    ]
    
    # objects = GameManager()
    number = models.IntegerField('Game No.', default=1,validators=[MinValueValidator(1), MaxValueValidator(16)], choices=GAME_NUMBERS)
    start_time = models.DateTimeField(blank=False, null=False)
    home_team = models.ForeignKey(Team, related_name="home_team", on_delete=models.SET_NULL, null=True)
    visiting_team = models.ForeignKey(Team, related_name="visiting_team", on_delete=models.SET_NULL, null=True)
    home_score = models.PositiveSmallIntegerField(default=0)
    visitor_score = models.PositiveSmallIntegerField(default=0)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    week = models.ForeignKey(Week, on_delete=models.CASCADE, null=False)
    is_regulation_tie = models.BooleanField(default=False)
    game_status = models.ForeignKey(GameStatus, on_delete=models.CASCADE, blank=False, null=False, default=1)

    def is_not_yet_started(self):
        return is_game_not_yet_started(self.start_time)

    def is_complete(self):
        scores_are_not_zeroes = self.home_score != 0 and self.visitor_score != 0
        time_passed = has_start_time_passed(self.start_time)
        so_what = time_passed and scores_are_not_zeroes
        return so_what

    def is_underway(self):
        scores_are_zeroes = self.home_score == 0 and self.visitor_score == 0
        return has_start_time_passed(self.start_time) and scores_are_zeroes      

    def is_home_win(self):
        return self.home_score > self.visitor_score

    def is_visitor_win(self):
        return self.home_score < self.visitor_score

    def is_within_three(self):
        return (abs(self.home_score - self.visitor_score) <= 3)

    def is_reg_tie(self):
        return self.is_regulation_tie

    def is_overtime_tie(self):
        return self.home_score == self.visitor_score

    def __str__(self):
        return '%s : %s) %s @ %s  Kick-off: %s in %s' % (self.week, self.number, self.visiting_team.name, self.home_team.name, self.start_time.strftime("%Y-%m-%d %H:%M"), self.city.name)

    def game_no(self):
        return '%s) %s - %s' % (self.number, self.week.week_type, self.week.name)

    def game_with_results(self):
        week_type_color = 'blue'
        if self.week.week_type.id == 1:
            week_type_color = 'green'
        elif self.week.week_type.id == 3:
            week_type_color = 'red'  

        scores_are_not_zeroes = self.home_score != 0 and self.visitor_score != 0

        is_ot_tie = scores_are_not_zeroes and (self.home_score == self.visitor_score)
        
        is_within_three = scores_are_not_zeroes and (abs(self.home_score - self.visitor_score) <= 3)

        if is_ot_tie :
            return format_html('<span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>&#09;is at&#09;</span><span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>&#09;&#09;<span style="color:green;">[ WITHIN THREE ]</span>&#09;&#09;<span style="color:green;">[ REG TIE ]</span>&#09;&#09;<span style="color:green;">[ OT TIE ]</span>',
            self.visiting_team.color_01,
            self.visiting_team.name, 
            self.visiting_team.color_01,
            self.visitor_score, 
            self.home_team.color_01, 
            self.home_team.name,  
            self.home_team.color_01,           
            self.home_score)
        elif self.is_regulation_tie and is_within_three:
            return format_html('<span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>&#09;is at&#09;</span><span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>&#09;&#09;<span style="color:green;">[ REG TIE ]</span>&#09;&#09;<span style="color:green;">[ WITHIN THREE ]</span>',
            self.visiting_team.color_01,
            self.visiting_team.name, 
            self.visiting_team.color_01,
            self.visitor_score, 
            self.home_team.color_01, 
            self.home_team.name,  
            self.home_team.color_01,           
            self.home_score)            
        elif is_within_three:
            return format_html('<span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>&#09;is at&#09;</span><span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>&#09;&#09;<span style="color:green;">[ WITHIN THREE ]</span>',
            self.visiting_team.color_01,
            self.visiting_team.name, 
            self.visiting_team.color_01,
            self.visitor_score, 
            self.home_team.color_01, 
            self.home_team.name,  
            self.home_team.color_01,           
            self.home_score)
        elif self.is_regulation_tie:
            return format_html('<span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>&#09;is at&#09;</span><span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>&#09;&#09;<span style="color:green;">[ REG TIE ]</span>',
            self.visiting_team.color_01,
            self.visiting_team.name, 
            self.visiting_team.color_01,
            self.visitor_score, 
            self.home_team.color_01, 
            self.home_team.name,  
            self.home_team.color_01,           
            self.home_score)
        else :
            return format_html('<span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>&#09;is at&#09;</span><span style="color:{};">{}</span>&#09;<span style="color:{};">( {} )</span>',
            self.visiting_team.color_01,
            self.visiting_team.name, 
            self.visiting_team.color_01,
            self.visitor_score,             
            self.home_team.color_01, 
            self.home_team.name,
            self.home_team.color_01, 
            self.home_score)

        class Meta:
            ordering = ['number']            
            verbose_name_plural = 'Scores'
 
class Pick(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    score = models.PositiveSmallIntegerField(default=0)
    pick_type = models.ForeignKey(PickType, on_delete=models.CASCADE, null=False, default=1)
    last_saved_date = models.DateTimeField(auto_now=True)

    def is_home_win(self):
        return self.pick_type.id == 2

    def is_visitor_win(self):
        return self.pick_type.id == 3

    def is_within_three(self):
        return self.pick_type.id == 4

    def is_regulation_tie(self):
        return self.pick_type.id == 5

    def is_overtime_tie(self):
        return self.pick_type.id == 6

    def __str__(self):
        return self.pick_type.name
        # return '%s : %s' % (self.game.__str__, self.pick_type.__str__)

class Fee(models.Model):
    amount = models.DecimalField('Amount CAD', max_digits=5, decimal_places=2, null=False, default=50.00)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=False)
    local_amount = models.DecimalField('Amount in that Country', max_digits=5, decimal_places=2, null=False)
    exchange_source = models.CharField(max_length=50)
    exchange_rate_date = models.DateField(null=True)

    def label_for_local_amount(self):
        return 'Amount in %s' % (self.country.name)

    local_amount.short_description = 'Uh hi...'
    
    def __str__(self):
        return '%s %s %s as per %s on %s' % (self.amount, self.country.name, self.local_amount, self.exchange_source, self.exchange_rate_date)

class PageLayoutType(models.Model):
    GRID = 'Grid'
    LIST = 'List'
    SMALL = 'Compact'

    LAYOUT_TYPES = [
        (GRID, 'Grid'),
        (LIST, 'List'),
        (SMALL, 'Compact')
    ]
    name = models.CharField(max_length=12, blank=False, null=False, default=LIST, choices=LAYOUT_TYPES)

    def __str__(self):
        return self.name

class Preferences(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    picks_page_layout_type = models.ForeignKey(PageLayoutType, on_delete=models.CASCADE, related_name='picks_page_layout_type')
    winners_page_layout_type = models.ForeignKey(PageLayoutType, on_delete=models.CASCADE, blank=False, null=False, default=1, related_name='winners_page_layout_type')
    standings_page_layout_type = models.ForeignKey(PageLayoutType, on_delete=models.CASCADE, blank=False, null=False, default=1, related_name='standings_page_layout_type')

    def __str__(self):
        return self.picks_page_layout_type.name

    class Meta:
        verbose_name = 'Preferences'
        verbose_name_plural = "Preferences"

class Standings(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    pre_hof = models.PositiveSmallIntegerField(default=0)
    pre_week_1 = models.PositiveSmallIntegerField(default=0)
    pre_week_2 = models.PositiveSmallIntegerField(default=0)
    pre_week_3 = models.PositiveSmallIntegerField(default=0)
    pre_week_4 = models.PositiveSmallIntegerField(default=0)
    pre_total = models.PositiveSmallIntegerField(default=0)
    reg_week_1 = models.PositiveSmallIntegerField(default=0)
    reg_week_2 = models.PositiveSmallIntegerField(default=0)
    reg_week_3 = models.PositiveSmallIntegerField(default=0)
    reg_week_4 = models.PositiveSmallIntegerField(default=0)
    reg_week_5 = models.PositiveSmallIntegerField(default=0)
    reg_week_6 = models.PositiveSmallIntegerField(default=0)
    reg_week_7 = models.PositiveSmallIntegerField(default=0)
    reg_week_8 = models.PositiveSmallIntegerField(default=0)
    reg_week_9 = models.PositiveSmallIntegerField(default=0)
    reg_week_10 = models.PositiveSmallIntegerField(default=0)
    reg_week_11 = models.PositiveSmallIntegerField(default=0)
    reg_week_12 = models.PositiveSmallIntegerField(default=0)
    reg_week_13 = models.PositiveSmallIntegerField(default=0)
    reg_week_14 = models.PositiveSmallIntegerField(default=0)
    reg_week_15 = models.PositiveSmallIntegerField(default=0)
    reg_week_16 = models.PositiveSmallIntegerField(default=0)
    reg_week_17 = models.PositiveSmallIntegerField(default=0)
    reg_total = models.PositiveSmallIntegerField(default=0)
    post_week_1 = models.PositiveSmallIntegerField(default=0)
    post_week_2 = models.PositiveSmallIntegerField(default=0)
    post_week_3 = models.PositiveSmallIntegerField(default=0)
    post_week_4 = models.PositiveSmallIntegerField(default=0)
    post_total = models.PositiveSmallIntegerField(default=0)
    overall_total = models.PositiveSmallIntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'Standings'

def update_weeks_only_one_active(sender, instance, **kwargs):
    if instance.is_active:
        Week.objects.all().exclude(pk=instance.pk).update(is_active=False)

post_save.connect(update_weeks_only_one_active, sender=Week)

def create_picks_for_new_user(sender, **kwargs):
    try:
        games = Game.objects.all()

        for g in games:
            no_pick = PickType.objects.get(id=1) 

            saved_user = kwargs['instance']

            if not Pick.objects.filter(game_id=g.id, user_id=saved_user.id).exists():
                try:
                    pick = Pick(game=g, user=saved_user, score=0, pick_type=no_pick)
                    pick.save()
                except IntegrityError as ie:
                    print(ie)

    except Exception as e: print(e)
    
def create_payer_audit_new_user(sender, **kwargs):
    try:
        saved_user = kwargs['instance']
        
        if not PayerAudit.objects.filter(user_id=saved_user.id).exists():
            try:
                payer_audit = PayerAudit(user_id=saved_user.id)
                payer_audit.save()

                alert_new_user = Alert(user_id=saved_user.id, message='Welcome to this year\'s football pool. This is a welcome alert. Click the =>\'x\' to delete it.', alert_level_id=1)
                alert_new_user.save()

                prefs = Preferences(user_id=saved_user.id, picks_page_layout_type_id=1, winners_page_layout_type_id=1)
                prefs.save()

            except IntegrityError as ie:
                print(ie)

    except Exception as e: print(e)
    
post_save.connect(create_picks_for_new_user, sender=CustomUser)
post_save.connect(create_payer_audit_new_user, sender=CustomUser)

def create_payer_audit_for_new_user(sender, instance, **kwargs):
    if not PayerAudit.objects.filter(user_id=instance.id).exists():
        try:
            pa = PayerAudit(user=instance, has_paid=False)
            pa.save()
        except IntegrityError as ie:
            print(ie)

post_save.connect(create_payer_audit_for_new_user, sender=CustomUser)

def update_seasons_only_one_active(sender, instance, **kwargs):
    if instance.is_active:
        Season.objects.all().exclude(pk=instance.pk).update(is_active=False)

post_save.connect(update_seasons_only_one_active, sender=Season)

def create_winner_for_week(week):
    win = Winner(week=week)
    win.save()

def create_game(number, week, start_time, city_id):
    g = Game(number=number, week=week, start_time=start_time, home_team_id = 1, visiting_team_id = 1, city_id = city_id, game_status_id = 1)
    g.save()

def create_weeks_on_season_create(sender, instance, **kwargs):

    try:
        saved_season = instance
        
        if not Week.objects.filter(season_id=saved_season.id).exists():
            try:
                pre = WeekType.objects.get(id=1)

                if pre.is_active:
                
                    now = get_now()
                    nowPlusSeven = now + timedelta(days=7)
                    w = Week(name='Hall of Fame', effective_date=now, effective_end_date=nowPlusSeven, is_active=True, week_type=pre, season=saved_season)
                    w.save()
                    create_winner_for_week(w)
                    create_game(1, w, now, 1)

                    now = nowPlusSeven + timedelta(days=1)
                    nowPlusSeven = now + timedelta(days=7)
                    w = Week(name='Week 1', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=pre, season=saved_season)
                    w.save()
                    create_winner_for_week(w)
                    for x in range(1, 17):
                        create_game(x, w, now, 1)                

                    now = nowPlusSeven + timedelta(days=1)
                    nowPlusSeven = now + timedelta(days=7)
                    w = Week(name='Week 2', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=pre, season=saved_season)
                    w.save()
                    create_winner_for_week(w)
                    for x in range(1, 17):
                        create_game(x, w, now, 1)

                    now = nowPlusSeven + timedelta(days=1)
                    nowPlusSeven = now + timedelta(days=7)
                    w = Week(name='Week 3', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=pre, season=saved_season)
                    w.save()
                    for x in range(1, 17):
                        create_game(x, w, now, 1)

                    now = nowPlusSeven + timedelta(days=1)
                    nowPlusSeven = now + timedelta(days=7)
                    w = Week(name='Week 4', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=pre, season=saved_season)
                    w.save()
                    for x in range(1, 17):
                        create_game(x, w, now, 1)                
                
                reg = WeekType.objects.get(id=2)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 1', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 2', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)                
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 3', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 4', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                for x in range(1, 16):
                    create_game(x, w, now, 1)                

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 5', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                for x in range(1, 16):
                    create_game(x, w, now, 1)
                
                create_winner_for_week(w)
                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 6', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                for x in range(1, 15):
                    create_game(x, w, now, 1)
                
                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 7', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 15):
                    create_game(x, w, now, 1)
                
                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 8', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 16):
                    create_game(x, w, now, 1)
                
                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 9', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 10', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 14):
                    create_game(x, w, now, 1)
                
                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 11', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 12', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 15):
                    create_game(x, w, now, 1)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 13', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 14', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 15', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)
                
                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 16', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)

                now = nowPlusSeven + timedelta(days=1)
                nowPlusSeven = now + timedelta(days=7)
                w = Week(name='Week 17', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=reg, season=saved_season)
                w.save()
                create_winner_for_week(w)
                for x in range(1, 17):
                    create_game(x, w, now, 1)

                post = WeekType.objects.get(id=3)

                if post.is_active:

                    now = nowPlusSeven + timedelta(days=1)
                    nowPlusSeven = now + timedelta(days=7)
                    w = Week(name='Wild Card Weekend', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=post, season=saved_season)
                    w.save()
                    create_winner_for_week(w)
                    for x in range(1, 5):
                        create_game(x, w, now, 1)

                    now = nowPlusSeven + timedelta(days=1)
                    nowPlusSeven = now + timedelta(days=7)
                    w = Week(name='Divisional Playoffs', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=post, season=saved_season)
                    w.save()
                    create_winner_for_week(w)
                    for x in range(1, 5):
                        create_game(x, w, now, 1)

                    now = nowPlusSeven + timedelta(days=1)
                    nowPlusSeven = now + timedelta(days=7)
                    w = Week(name='Conference Championships', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=post, season=saved_season)
                    w.save()
                    create_winner_for_week(w)
                    create_game(1, w, now, 1)
                    create_game(2, w, now, 1)

                    now = nowPlusSeven + timedelta(days=1)
                    nowPlusSeven = now + timedelta(days=14)
                    w = Week(name='Super Bowl', effective_date=now, effective_end_date=nowPlusSeven, is_active=False, week_type=post, season=saved_season)
                    w.save()
                    create_winner_for_week(w)
                    create_game(1, w, now, 1)                    
                
            except IntegrityError as ie:
                print('IntegrityError creating Season')
                print(ie)
    except Exception as e: 
        print('Exception creating Season')
        print(e)

post_save.connect(create_weeks_on_season_create, sender=Season)

def getAllUsersExceptSuperAdmin():
    return CustomUser.objects.all()

def save_picks_after_saving_game(sender, **kwargs):

    try:
        users = getAllUsersExceptSuperAdmin()

        saved_game = kwargs['instance']
        Pick.objects.filter(game_id=saved_game.id).update(score=0)
        
        for u in users:            
            pick, created = Pick.objects.get_or_create(game_id=saved_game.id, user_id=u.id)            
            if created:
                pass
            else:  
                if saved_game.is_home_win() and pick.is_home_win():
                    pick.score = 1
                    pick.save()

                if saved_game.is_visitor_win() and pick.is_visitor_win():
                    pick.score = 1
                    pick.save()

                if saved_game.is_within_three() and pick.is_within_three():
                    pick.score = 2
                    pick.save()

                if saved_game.is_reg_tie() and pick.is_regulation_tie():
                    pick.score = 3
                    pick.save()

                if saved_game.is_overtime_tie() and pick.is_overtime_tie():
                    pick.score = 5
                    pick.save()

    except Exception as e: print(e)

post_save.connect(save_picks_after_saving_game, sender=Game)