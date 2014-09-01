from django.contrib import admin
from zadaci.models import Zadatak, Profil, Glas, Aktivnost


class ZadatakAdmin(admin.ModelAdmin):
    list_display = ['ime', 'dodao',
              'tezina', 'tezina_br_glasova',
              'kvaliteta', 'kvaliteta_br_glasova',
              'br_todo', 'br_rijesio', 'br_najdrazi',
              'vrijeme', 'obiljezja']
    search_fields = ['ime']


class ProfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'ime', 'prezime', 'spol', 'vrijeme_registracije']


class GlasAdmin(admin.ModelAdmin):
    list_display = ['user', 'zadatak', 'tip_glasa', 'vrijednost']


class AktivnostAdmin(admin.ModelAdmin):
    list_display = ['user', 'tip_aktivnosti', 'zadatak', 'vrijeme']


admin.site.register(Zadatak, ZadatakAdmin)
admin.site.register(Profil, ProfilAdmin)
admin.site.register(Glas, GlasAdmin)
admin.site.register(Aktivnost, AktivnostAdmin)
