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

    # Obrisi prijasnju listu.
    Aktivnost.objects.filter(
        user=request.user, zadatak=zadatak,
        tip_aktivnosti__in=['todo', 'rijesio', 'najdrazi']).delete()

    # Zabiljezi novu listu.
    if lista != "":
        aktivnost = Aktivnost(user=request.user, zadatak=zadatak,
                              tip_aktivnosti=lista)
        aktivnost.save()

    # Azuriraj zadatak.
    zadatak.br_todo = Aktivnost.objects.filter(
        zadatak=zadatak, tip_aktivnosti='todo').count()
    zadatak.br_rijesio = Aktivnost.objects.filter(
        zadatak=zadatak, tip_aktivnosti='rijesio').count()
    zadatak.br_najdrazi = Aktivnost.objects.filter(
        zadatak=zadatak, tip_aktivnosti='najdrazi').count()
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
