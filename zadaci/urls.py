from django.conf.urls import patterns, url
from zadaci import views

urlpatterns = patterns(
    '',
    url(r'^$', views.homepage, name='homepage'),

    url(r'^dodaj/$', views.dodaj_zadatak, name='dodaj_zadatak'),
    url(r'^zadaci/$', views.zadaci.as_view(), name='zadaci'),
    url(r'^random/$', views.slucajan_zadatak, name='slucajan_zadatak'),
    url(r'^tutorijali/$', views.tutorijali, name='tutorijali'),
    url(r'^korisnici/$', views.korisnici.as_view(), name='korisnici'),
    url(r'^uredi_profil/$', views.uredi_profil, name='uredi_profil'),
    url(r'^odjava/$', views.odjava, name='odjava'),
    url(r'^obiljezja/$', views.obiljezja, name='obiljezja'),

    # npr. /zadatak/3/
    url(r'^zadatak/(?P<pk>\d+)/$', views.zadatak.as_view(), name='zadatak'),

    # npr. /profil/3/
    url(r'^profil/(?P<pk>\d+)/$', views.profil.as_view(), name='profil'),

    # npr. /dodaj/3/ (kada korisnik uredjuje zadatak)
    url(r'^dodaj/(?P<zadatak_id>\d+)/$',
        views.dodaj_zadatak, name='dodaj_zadatak'),

    # Kad korisnik aktivira svoj racun, preusmjeri ga na uredjivanje profila.
    url(r'^accounts/activate/complete/$', views.uredi_profil,
        name='activation_complete')
)
