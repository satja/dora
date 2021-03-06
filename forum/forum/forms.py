from django import forms
from django.utils.translation import ugettext as _


class CreateThreadForm(forms.Form):
    title = forms.CharField(label=_("Naslov"), max_length=100)
    body = forms.CharField(
        label=_("Tekst"),
        widget=forms.Textarea(attrs={'rows': 8, 'cols': 100})
    )
    subscribe = forms.BooleanField(
        label=_("Pretplati se e-mailom na nove odgovore?"),
        required=False,
    )


class ReplyForm(forms.Form):
    body = forms.CharField(
        label=_("Tekst"),
        widget=forms.Textarea(attrs={'rows': 8, 'cols': 100})
    )
    subscribe = forms.BooleanField(
        label=_("Pretplati se e-mailom na nove odgovore?"),
        required=False,
    )
