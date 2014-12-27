from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib import admin

admin.autodiscover()
dajaxice_autodiscover()

urlpatterns = patterns(
    '',
    url(r'', include('zadaci.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^tagging_autocomplete/', include('tagging_autocomplete.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^forum/', include('forum.urls')),
)

urlpatterns += staticfiles_urlpatterns()

patterns += (
    url(r'^passreset/$', auth_views.password_reset, name='forgot_password1'),
    url(r'^passresetdone/$',
        auth_views.password_reset_done, name='forgot_password2'),
    url(r'^passresetconfirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$',
        auth_views.password_reset_confirm, name='forgot_password3'),
    url(r'^passresetcomplete/$',
        auth_views.password_reset_complete, name='forgot_password4'),
)

# Iz http://stackoverflow.com/questions/5517950/django-media-url-and-media-root
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}))
