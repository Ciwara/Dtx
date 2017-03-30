"""doctix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include, static
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib import admin
from doctix import views
from fondasms import views as fonda_views
from .forms import LoginForm


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^home/$', TemplateView.as_view(template_name="homepage.html"),),
    url(r'^fullcalendar/',
        TemplateView.as_view(template_name="fullcalendar.html"), name='fullcalendar'),
    url(r'^schedule/', include('schedule.urls')),
    url(r'^sms-sender/$', views.smssender, name='smssender'),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'login.html',
     'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    # Android API
    url(r'^fondasms/?$', fonda_views.fondasms_handler,
        {'handler_module': 'doctix.sms.fondasms_handlers',
         'send_automatic_reply': False,
         'automatic_reply_via_handler': False,
         'automatic_reply_text': ("Merci.")},
        name='fondasms'),

    url(r'^fondasms/test/?$',
        TemplateView.as_view(template_name="fondasms_tester.html"),
        name='fondasms_tester'),
]

if settings.DEBUG:
    print("DEBUG")
    # urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += patterns(
    #     '',
    #     url(
    #         r'^site_media/(?P<path>.*)$',
    #         'django.views.static.serve',
    #         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    # )
