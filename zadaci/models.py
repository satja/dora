# -*- coding: utf-8 -*-

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import models
import datetime
from tagging.models import Tag
from tagging_autocomplete.models import TagAutocompleteField
from django.dispatch import receiver
from django_comments.signals import comment_was_posted
from registration.signals import user_activated


class Zadatak(models.Model):
    """Definira zadatak u bazi podataka."""
    ime = models.CharField(max_length=50, unique=True)
    link = models.URLField()
    izvor = models.CharField(max_length=100, blank=True)
    tezina = models.FloatField(null=True, blank=True)
    tezina_br_glasova = models.IntegerField(default=0)
    kvaliteta = models.FloatField(null=True, blank=True)
    kvaliteta_br_glasova = models.IntegerField(default=0)
    dodao = models.ForeignKey(User, related_name='dodao')
    br_todo = models.IntegerField(default=0)
    br_rijesio = models.IntegerField(default=0)
    br_najdrazi = models.IntegerField(default=0)
    vrijeme = models.DateTimeField(default=datetime.datetime.now)
    obiljezja = TagAutocompleteField()

    def __str__(self):
        return self.ime

    def get_tags(self):
        """Dobavlja obiljezja zadatka."""
        return Tag.objects.get_for_object(self)

    class Meta:
        ordering = ('-kvaliteta', '-kvaliteta_br_glasova',
                    '-tezina', '-tezina_br_glasova', '-vrijeme',)

    def delete(self):
        """Brine da se i obiljezja zadatka obrisu."""
        Tag.objects.update_tags(self, None)
        super(Zadatak, self).delete()


class Profil(models.Model):
    """Definira profil u bazi podataka."""
    user = models.OneToOneField(User)
    ime = models.CharField(max_length=20, blank=True)
    prezime = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    slika = models.ImageField(upload_to='profile_images', blank=True)
    moto = models.CharField(max_length=1000, blank=True)

    SPOLOVI = (('f', 'Žensko'), ('m', 'Muško'))
    spol = models.CharField(max_length=1, choices=SPOLOVI, blank=True)

    vrijeme_registracije = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.user.username


class Glas(models.Model):
    """Predstavlja jedno glasovanje korisnika za tezinu ili kvalitetu zadatka.
    """
    user = models.ForeignKey(User)
    zadatak = models.ForeignKey(Zadatak)
    TIPOVI_GLASA = (('tezina', 'tezina'), ('kvaliteta', 'kvaliteta'))
    tip_glasa = models.CharField(max_length=10, choices=TIPOVI_GLASA)
    vrijednost = models.FloatField()

    def __str__(self):
        return self.user.username + ' ' + self.zadatak.ime + ' '\
            + self.tip_glasa + ' ' + str(self.vrijednost)


class Aktivnost(models.Model):
    """Sto je koji korisnik kada napravio."""
    user = models.ForeignKey(User)
    zadatak = models.ForeignKey(Zadatak, null=True, blank=True)
    TIPOVI_AKTIVNOSTI = (('dodao', 'je dodao zadatak'),
                         ('izmijenio', 'je izmijenio zadatak'),
                         ('komentirao', 'je komentirao zadatak'),
                         ('rijesio', 'je riješio zadatak'),
                         ('todo', 'je stavio na TODO listu zadatak'),
                         ('najdrazi', 'je stavio na listu najdražih zadataka'),
                         ('registrirao', 'se registrirao'),
                         )
    tip_aktivnosti = models.CharField(max_length=11, choices=TIPOVI_AKTIVNOSTI)
    vrijeme = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        prikaz = self.user.username + ' ' + self.get_tip_aktivnosti_display()
        if not self.zadatak:
            return prikaz
        return prikaz + ' ' + self.zadatak.ime


@receiver(comment_was_posted)
def novi_komentar(sender, comment, **kwargs):
    """Reagira na dodavanje novog komentara: biljezi aktivnost."""
    korisnik = comment.user
    zadatak = comment.content_type.get_object_for_this_type(
        pk=comment.object_pk)
    aktivnost = Aktivnost(user=korisnik, zadatak=zadatak,
                          tip_aktivnosti='komentirao')
    aktivnost.save()


@receiver(user_activated)
def novi_korisnik(sender, user, request, **kwargs):
    """Reagira na aktivaciju racuna: stvara novi profil,
    biljezi aktivnost (registraciju), odmah logira korisnika.
    """
    profil, created = Profil.objects.get_or_create(user=user)
    if not created:
        return

    aktivnost = Aktivnost(user=user, tip_aktivnosti='registrirao')
    aktivnost.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
