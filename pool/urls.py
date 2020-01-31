import django
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import CreateUser, EditUser, TalkView, HomePageView, PoolMembers, NewsItemsView, RulesView, FeesView, PicksView, WinnersView, AdminNoPicks, StandingsView
from . import views

def custom_page_not_found(request):
    return django.views.defaults.page_not_found(request, None)

def custom_server_error(request):
    return django.views.defaults.server_error(request)
    
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('set_timezone/', views.set_timezone, name='set_timezone'),
    path('create_user/', CreateUser.as_view(), name='create_user'),
    path('edit_user/', EditUser.as_view(), name='edit_user'),
    path('talk/', TalkView.as_view(), name='talk'),
    path('home/', HomePageView.as_view(), name='home'),
    path('members/', PoolMembers.as_view(), name='members'),    
    path('delete_alert/<int:pk>/', views.delete_alert, name='delete_alert'),
    path('delete_talk/<int:pk>/', views.delete_talk, name='delete_talk'),
    path('make_pick/<int:pk>/<int:pt_pk>', views.make_pick, name='make_pick'),
    path('news/', NewsItemsView.as_view(), name='news'),
    path('rules/', RulesView.as_view(), name='rules'),
    path('fees/', FeesView.as_view(), name='fees'),
    path('picks/', PicksView.as_view(), name='picks'),
    path('winners/', WinnersView.as_view(), name='winners'),
    path('standings/', StandingsView.as_view(), name='standings'),
    path('change_week_type_for_picks/<pk>', views.change_week_type_for_picks, name='change_week_type_for_picks'),
    path('change_layout_type_for_picks/<pk>', views.change_layout_type_for_picks, name='change_layout_type_for_picks'),
    path('change_selected_week_for_picks/<pk>', views.change_selected_week_for_picks, name='change_selected_week_for_picks'),
    path('admin_no_picks', AdminNoPicks.as_view(), name='admin_no_picks'),
    path('send_email_reminder', views.send_email_reminder, name='send_email_reminder'),
    path("404/", custom_page_not_found),
    path("500/", custom_server_error),




]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




# handler404 = 'pool.views.error_404'
# handler500 = 'pool.views.error_500'
# handler403 = 'myappname.views.error_403'
# handler400 = 'myappname.views.error_400'