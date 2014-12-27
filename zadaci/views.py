# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from zadaci.models import Zadatak, Profil, Aktivnost, Glas
from tagging.models import TaggedItem
from zadaci.forms import ZadatakForm, ProfilForm, ObiljezjaForm
from zadaci.ajax import glasuj
from ordered_listview.views import OrderedListView
import random
import re


class zadatak(generic.DetailView):
    """Klasa koja se bavi prikazom pojedinacnog zadatka."""
    model = Zadatak
    template_name = 'zadaci/zadatak.html'

    def get_context_data(self, **kwargs):
        """Iz baze vadi kontekst zadatka koji ce se prikazati."""

        # Prvo pozovi baznu funkciju za glavni kontekst (iz tablice Zadatak).
        context = super(zadatak, self).get_context_data(**kwargs)
        ovaj_zadatak = context['zadatak']

        # Vadimo ekstra kontekst zadatka: tko ga je stavio na koju listu.
        for tip_aktivnosti in ['rijesio', 'todo', 'najdrazi']:
            korisnici_ids = Aktivnost.objects.filter(
                zadatak=ovaj_zadatak, tip_aktivnosti=tip_aktivnosti
            ).values_list('user', flat=True).distinct()
            context[tip_aktivnosti] = User.objects.filter(pk__in=korisnici_ids)

        # A sada kontekst vezan za korisnika o cijem requestu se radi.
        korisnik = self.request.user
        if korisnik.is_authenticated():
            # Je li korisnik stavio ovaj zadatak na listu
            # todo ili rijesenih zadataka?
            lista = Aktivnost.objects.filter(
                user=korisnik, zadatak=ovaj_zadatak,
                tip_aktivnosti__in=['todo', 'rijesio']
            ).values_list('tip_aktivnosti', flat=True)
            if lista:
                context['lista'] = lista[0]

            # A je li mu ovo jedan od najdrazih zadataka?
            context['je_li_najdrazi'] = Aktivnost.objects.filter(
                user=korisnik, zadatak=ovaj_zadatak, tip_aktivnosti='najdrazi'
            ).count()

            # Je li korisnik glasao za tezinu/kvalitetu?
            for tip_glasa in ['tezina', 'kvaliteta']:
                vrijednost_glasa = Glas.objects.filter(
                    user=korisnik, zadatak=ovaj_zadatak,
                    tip_glasa=tip_glasa
                ).values_list('vrijednost', flat=True)
                if vrijednost_glasa:
                    context[tip_glasa] = int(vrijednost_glasa[0])

        return context


class zadaci(OrderedListView):
    """Klasa koja se bavi prikazom liste zadataka i rezultata pretrage."""
    template_name = 'zadaci/zadaci.html'
    context_object_name = 'zadaci'
    model = Zadatak

    allowed_order_by = [
        ('-kvaliteta', 'Kvaliteta'),
        ('tezina', 'Težina (uzlazno)'),
        ('-tezina', 'Težina (silazno)'),
        ('-vrijeme', 'Vrijeme dodavanja (silazno)'),
        ('vrijeme', 'Vrijeme dodavanja (uzlazno)'),
    ]
    default_order_by = '-kvaliteta'
    paginate_by = 30

    def get_queryset(self):
        """Dobavljanje liste ovisno o pretrazi."""
        ime = self.request.GET.get('ime', '')
        link = self.request.GET.get('link', '')
        izvor = self.request.GET.get('izvor', '')
        tezina_min = self.request.GET.get('tezina_min', 1)
        tezina_max = self.request.GET.get('tezina_max', 10)
        obiljezja = self.request.GET.get('obiljezja', '')
        if obiljezja:
            rezultati = TaggedItem.objects.get_by_model(
                Zadatak, re.split(", |,| ", obiljezja))
        else:
            rezultati = Zadatak.objects.all()
        rezultati = rezultati.filter(
            ime__icontains=ime,
            link__icontains=link,
            izvor__icontains=izvor,
            # Ukljuci samo one kojima je tezina <= tezina_max.
            tezina__lte=tezina_max,
        ).exclude(
            # Iskljuci one kojima je 0 < tezina < tezina_min.
            # (Na ovaj nacin ne izbacujemo one kojima tezina nije postavljena.)
            tezina__gt=0,
            tezina__lt=tezina_min,
        )
        return rezultati.order_by(self.order_by)


class profil(generic.DetailView):
    """Klasa koja se bavi prikazom pojedinacnog profila."""
    model = Profil
    template_name = 'zadaci/profil.html'

    def get_context_data(self, **kwargs):
        """Iz baze vadi kontekst profila koji ce se prikazati."""

        # Prvo pozovi baznu funkciju za glavni kontekst (iz tablice Profil).
        context = super(profil, self).get_context_data(**kwargs)
        korisnik = context['profil'].user

        # Dodaj ekstra kontekst: koje je zadatke korisnik stavio na koju listu.
        for tip_aktivnosti in ['dodao', 'komentirao',
                               'rijesio', 'todo', 'najdrazi']:
            zadaci_ids = Aktivnost.objects.filter(
                user=korisnik, tip_aktivnosti=tip_aktivnosti
            ).values_list('zadatak', flat=True).distinct()
            context[tip_aktivnosti] = Zadatak.objects.filter(pk__in=zadaci_ids)

        # Sto je korisnik nedavno radio?
        context['nedavno'] = Aktivnost.objects.filter(
            user=korisnik).order_by('-vrijeme')[:17]

        return context


class korisnici(generic.ListView):
    """Klasa koja se bavi prikazom liste korisnika."""
    template_name = 'zadaci/korisnici.html'
    context_object_name = 'profili'
    model = Profil


def homepage(request):
    """Renderira homepage.
    Dodatni kontekst:
        - forma za obiljezja (sluzi za autocomplete u pretrazi),
        - nedavne aktivnosti.
    """
    return render(request, 'zadaci/homepage.html', {
        'obiljezja': ObiljezjaForm(),
        'nedavno': Aktivnost.objects.all().order_by('-vrijeme')[:17],
    })


@login_required
def dodaj_zadatak(request, zadatak_id=None):
    """Renderira formu za dodavanje i izmjenu zadatka te reagira na njezin unos.
    """
    # Je li ovo zahtjev za izmjenom zadatka?
    if zadatak_id:
        izmjena = True
    else:
        izmjena = False

    if izmjena:
        zadatak = get_object_or_404(Zadatak, pk=int(zadatak_id))

        # Ako korisnik ne smije mijenjati ovaj zadatak...
        if not request.user.is_staff and zadatak.dodao != request.user:
            raise Http404

        # Zeli li korisnik obrisati zadatak?
        if request.method == 'POST' and request.POST.get('obrisi', '') and\
                request.POST.get('sigurno_obrisi', ''):
            zadatak.delete()
            return HttpResponseRedirect('/')

    else:
        zadatak = None

    # Jesam li submitao formu ili je tek dohvacam?
    # Ako je ovo submit:
    if request.method == 'POST':
        form = ZadatakForm(request.POST, instance=zadatak, izmjena=zadatak_id)
        if form.is_valid():
            # Spremi zadatak u bazu.
            zadatak = form.save(commit=False)
            zadatak.dodao = request.user
            zadatak.save()

            # Spremi aktivnost te glasove za tezinu i kvalitetu.
            if izmjena:
                tip_aktivnosti = 'izmijenio'
            else:
                tip_aktivnosti = 'dodao'
                if zadatak.tezina:
                    glasuj(request, zadatak.pk, 'tezina', zadatak.tezina)
                if zadatak.kvaliteta:
                    glasuj(request, zadatak.pk, 'kvaliteta', zadatak.kvaliteta)
            aktivnost = Aktivnost(user=request.user,
                                  zadatak=zadatak,
                                  tip_aktivnosti=tip_aktivnosti)
            aktivnost.save()

            # Je li korisnik stisnuo "Spremi" ili "Spremi i dodaj novi"?
            if request.POST.get('submit') == 'Spremi':
                return redirect('/zadatak/' + str(zadatak.pk))
            return redirect('/dodaj/')
        else:
            print form.errors

    # Ako ovo nije POST request:
    else:
        # Dohvacanje forme.
        if izmjena:
            form = ZadatakForm(instance=zadatak, izmjena=zadatak_id)
        else:
            form = ZadatakForm()

    return render(request, 'zadaci/dodaj.html', {
        'form': form,
        'nedavno': Aktivnost.objects.all().order_by('-vrijeme')[:17],
        'izmjena': izmjena})


@login_required
def uredi_profil(request):
    """Renderira formu za izmjenu profila te reagira na njezin unos."""
    ovaj_profil = request.user.profil

    # Ako je ovo vec submitana forma:
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=ovaj_profil)
        if form.is_valid():
            form.save()
            return redirect('/profil/' + str(ovaj_profil.pk))
        else:
            print form.errors

    # Ako korisnik tek dohvaca formu:
    else:
        form = ProfilForm(instance=ovaj_profil)

    return render(request, 'zadaci/uredi_profil.html', {
        'form': form,
        # Je li korisnik tek aktivirao svoj racun? Sluzi za ispis poruke o tome.
        'tek_aktiviran': 'activate' in request.path,
    })


def tutorijali(request):
    return render(request, "zadaci/tutorijali.html")


def slucajan_zadatak(request):
    """Preusmjerava na slucajan zadatak iz baze."""
    slucajan = random.choice(Zadatak.objects.all())
    return HttpResponseRedirect('/zadatak/' + str(slucajan.pk))


def obiljezja(request):
    """Renderira sva obiljezja zadataka koja postoje u bazi."""
    return render(request, "zadaci/sva_obiljezja.html")


@login_required
def odjava(request):
    """Odjavljuje korisnika. Prijavu i registraciju rjesava django-registration.
    """
    logout(request)
    return HttpResponseRedirect('/')


def tutorijal(request, ime_tutorijala):
    """Renderira tutorijal."""
    template = 'tutorijali/' + ime_tutorijala + '.html'
    return render(request, template)
