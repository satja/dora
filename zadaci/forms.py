# -*- coding: utf-8 -*-

from django import forms
from django.forms.extras.widgets import Select
from zadaci.models import Zadatak, Profil
from tagging.forms import TagField
from tagging_autocomplete.widgets import TagAutocomplete


class ZadatakForm(forms.ModelForm):
    """Forma za dodavanje i uredjivanje zadatka."""

    # Definirajmo polja za tezinu i kvalitetu zadatka; ostala polja automatski
    # se preuzimaju iz modela.
    tezina = forms.ChoiceField(choices=[(0, 'ne znam')] +
                               [(i, i) for i in range(1, 11)])
    kvaliteta = forms.ChoiceField(choices=[(0, 'ne znam')] +
                                  [(i, i) for i in range(1, 6)])

    def __init__(self, *args, **kwargs):
        # Treba li izbaciti polja za tezinu i kvalitetu? Da, ako samo
        # uredjujemo zadatak (jer korisnici glasuju za njih).
        izbaci_polja = kwargs.pop('izmjena', False)
        super(ZadatakForm, self).__init__(*args, **kwargs)
        self.fields['tezina'].required = False
        self.fields['kvaliteta'].required = False
        self.fields['obiljezja'].required = True
        if izbaci_polja:
            self.fields.pop('tezina')
            self.fields.pop('kvaliteta')

    class Meta:
        model = Zadatak
        fields = ('ime', 'link', 'izvor', 'tezina', 'kvaliteta', 'obiljezja')
        labels = {
            'ime': 'Ime zadatka',
            'link': 'Link na zadatak',
            'izvor': 'Izvor zadatka',
            # TODO: zasto se naredne dvije labele ignoriraju?
            # Je li to zbog drugacijega widgeta?
            'tezina': 'Težina (1-10)',
            'kvaliteta': 'Kvaliteta (1-5)',
        }
        VELICINA_POLJA = 50
        widgets = {
            'ime': forms.TextInput(attrs={
                'size': VELICINA_POLJA,
                'placeholder': 'obavezno',
            }),
            'link': forms.TextInput(attrs={
                'size': VELICINA_POLJA,
                'placeholder': 'Npr. http://www.spoj.com/problems/CAGES/',
            }),
            'izvor': forms.TextInput(attrs={
                'size': VELICINA_POLJA,
                'placeholder':
                'Npr. Hrvatska informatička olimpijada - HIO 2013.',
            }),
            'tezina': Select(attrs={'class': 'select'}),
            'kvaliteta': Select(attrs={'class': 'select'}),
        }

    obiljezja = TagField(
        label='Obilježja',
        widget=TagAutocomplete(attrs={
            'size': Meta.VELICINA_POLJA,
            'placeholder': 'obavezno (barem jedno)',
        }),
    )


class ObiljezjaForm(forms.Form):
    """Forma za unos obiljezja, postoji radi autocompletea."""
    obiljezja = TagField(widget=TagAutocomplete())


class ProfilForm(forms.ModelForm):
    """Forma za uredjivanje profila."""
    class Meta:
        model = Profil
        fields = ('ime', 'prezime', 'spol', 'website', 'slika', 'moto',)
        VELICINA_IMENA = 20
        VELICINA_POLJA = 50
        widgets = {
            'ime': forms.TextInput(attrs={'size': VELICINA_IMENA}),
            'prezime': forms.TextInput(attrs={'size': VELICINA_IMENA}),
            'website': forms.TextInput(attrs={'size': VELICINA_POLJA}),
            'moto': forms.TextInput(attrs={'size': VELICINA_POLJA}),
        }
