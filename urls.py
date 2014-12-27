from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib import admin

admin.autodiscover()
dajaxice_autodiscover()

urlpatterns = patterns(
    '',
    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/user/password/reset/done/'},
        name="password_reset"),
    url(r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        name='password_reset_done'),
    url(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/user/password/done/'},
        name='password_reset_confirm'),
    url(r'^user/password/done/$',
        'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),

    url(r'', include('zadaci.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^tagging_autocomplete/', include('tagging_autocomplete.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^forum/', include('forum.urls')),
)

urlpatterns += staticfiles_urlpatterns()

# Iz http://stackoverflow.com/questions/5517950/django-media-url-and-media-root
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}))
