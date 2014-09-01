from django.db.models import Avg
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from dajaxice.decorators import dajaxice_register
from django_comments.models import Comment
from zadaci.models import Zadatak, Glas, Aktivnost


@dajaxice_register
@login_required
def azuriraj_listu(request, zadatak_id, lista):
    """Azurira na kojoj se listi doticnoga korisnika nalazi doticni zadatak
    (TODO lista, lista rijesenih, lista najdrazih).
    """
    zadatak = Zadatak.objects.get(pk=zadatak_id)

    # Nadji prijasnju listu.
    prijasnja = Aktivnost.objects.filter(
        user=request.user, zadatak=zadatak,
        tip_aktivnosti__in=['todo', 'rijesio', 'najdrazi'])
    if prijasnja:
        bivsa_lista = prijasnja[0].tip_aktivnosti
        prijasnja.delete()
        # Azuriraj zadatak, tj. smanji mu broj doticnih listi.
        zadatak.br_todo -= (bivsa_lista == 'todo')
        zadatak.br_rijesio -= (bivsa_lista == 'rijesio')
        zadatak.br_najdrazi -= (bivsa_lista == 'najdrazi')

    # Zabiljezi novu listu.
    if lista != "":
        aktivnost = Aktivnost(user=request.user, zadatak=zadatak,
                              tip_aktivnosti=lista)
        aktivnost.save()
        zadatak.br_todo += (lista == 'todo')
        zadatak.br_rijesio += (lista == 'rijesio')
        zadatak.br_najdrazi += (lista == 'najdrazi')

    zadatak.save()


@dajaxice_register
@login_required
def glasuj(request, zadatak_id, tip_glasa, glas):
    """Biljezi korisnikov glas za tezinu ili kvalitetu zadatka.
    """
    zadatak = Zadatak.objects.get(pk=zadatak_id)

    # Je li korisnik vec glasao za ovo?
    postojeci_glas = Glas.objects.filter(user=request.user, zadatak=zadatak,
                                         tip_glasa=tip_glasa)
    if postojeci_glas.count() == 0:
        novi_glas = Glas(user=request.user, zadatak=zadatak,
                         tip_glasa=tip_glasa, vrijednost=glas)
    else:
        novi_glas = postojeci_glas[0]
        novi_glas.vrijednost = glas

    novi_glas.save()

    # Racunamo novi prosjecan glas za doticni zadatak.
    vrijednost = Glas.objects.filter(
        zadatak=zadatak, tip_glasa=tip_glasa).aggregate(Avg('vrijednost'))
    vrijednost = vrijednost['vrijednost__avg']
    br_glasova = Glas.objects.filter(
        zadatak=zadatak, tip_glasa=tip_glasa).count()

    # Azuriramo zadatak.
    if tip_glasa == 'tezina':
        zadatak.tezina = vrijednost
        zadatak.tezina_br_glasova = br_glasova
    elif tip_glasa == 'kvaliteta':
        zadatak.kvaliteta = vrijednost
        zadatak.kvaliteta_br_glasova = br_glasova
    else:
        raise Exception("Tip glasa mora biti 'tezina' ili 'kvaliteta'!")

    zadatak.save()

    return simplejson.dumps({'tip_glasa': tip_glasa,
                             'vrijednost': vrijednost,
                             'br_glasova': br_glasova})


@dajaxice_register
@login_required
def obrisi_komentar(request, komentar_id):
    """Brise komentar na zadatak."""
    komentar = Comment.objects.get(pk=komentar_id)
    if komentar.user == request.user or request.user.is_staff:
        komentar.is_removed = True
        komentar.save()
