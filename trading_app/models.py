from django.db import models
from django.db.models import Q


class Categorie(models.Model):
    nume = models.CharField(
        max_length=100,
        unique=True,  # Câmp unic (altul decât id)
        help_text="Numele categoriei TCG (ex: Pokémon, Yu-Gi-Oh!, Accesorii).",  # help_text (1/5)
        error_messages={  # Mesaje de eroare (1/5)
            'unique': "Există deja o categorie cu acest nume!",
            'max_length': "Numele categoriei nu poate depăși 100 de caractere."
        }
    )
    slug = models.SlugField(  # SlugField
        max_length=120,
        unique=True,
        help_text="Identificator unic pentru URL (generat fără spații).",  # help_text (2/5)
        error_messages={  # Mesaje de eroare (2/5)
            'unique': "Acest slug este deja folosit de altă categorie."
        }
    )
    descriere = models.TextField(
        null=True,   # Câmp null (1/5)
        blank=True,  # Permite loc liber în formularul admin
        default="Categorie standard de produse TCG."  # Default (1/4)
    )
    culoare = models.CharField(
        max_length=20,
        default="#2c3e50",  # Default (2/4)
        help_text="Codul hexazecimal al culorii asociate categoriei."  # help_text (3/5)
    )
    sigla = models.ImageField(  # ImageField
        upload_to='categorii_sigle/',
        null=True,   # Câmp null (2/5)
        blank=True
    )
    popularitate = models.IntegerField(
        default=1  # Default (3/4)
    )

    class Meta:
        verbose_name_plural = "Categorii"
        ordering = ['-popularitate', 'nume']  # Ordonare implicită (1/2)
        indexes = [
            models.Index(fields=['nume']),  # Index (1/4)
        ]
        constraints = [
            # Constrângere Q (1/5): Popularitatea trebuie să fie între 1 și 100
            models.CheckConstraint(
                condition=Q(popularitate__gte=1) & Q(popularitate__lte=100),
                name='check_popularitate_interval'
            )
        ]

    def __str__(self):
        return self.nume


class SetColectie(models.Model):
    nume_set = models.CharField(
        max_length=120,
        error_messages={  # Mesaje de eroare (3/5)
            'max_length': "Numele setului este prea lung (maxim 120 caractere)."
        }
    )
    an_aparitie = models.PositiveIntegerField(
        default=2026,  # Default (4/4)
        help_text="Anul oficial în care a fost lansat setul de cărți."  # help_text (4/5)
    )

    class Meta:
        verbose_name_plural = "Seturi Colecție"
        ordering = ['-an_aparitie', 'nume_set']  # Ordonare implicită (2/2)
        indexes = [
            models.Index(fields=['an_aparitie']),  # Index (2/4)
        ]
        constraints = [
            # Constrângere Q (2/5): Anul apariției să fie după primul TCG modern (1993)
            models.CheckConstraint(
                condition=Q(an_aparitie__gte=1993) & Q(an_aparitie__lte=2030),
                name='check_an_aparitie_valid'
            )
        ]

    def __str__(self):
        return f"{self.nume_set} ({self.an_aparitie})"


class Produs(models.Model):
    STARE_CHOICES = [  # Câmp cu choices
        ('nou', 'Nou / Sigilat (Mint)'),
        ('gradat', 'Gradat (PSA / Beckett)'),
        ('uzat', 'Uzat (Played)'),
    ]

    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        related_name='produse'
    )
    seturi = models.ManyToManyField(
        SetColectie,
        blank=True,
        related_name='produse'
    )
    titlu = models.CharField(
        max_length=150,
        error_messages={  # Mesaje de eroare (4/5)
            'blank': "Titlul produsului este obligatoriu!",
            'max_length': "Titlul depășește limita de 150 de caractere."
        }
    )
    pret = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Prețul produsului exprimat în RON (ex: 49.99)."  # help_text (5/5)
    )
    stoc = models.PositiveIntegerField(default=10)
    este_foarte_rar = models.BooleanField(default=False)
    data_lansare = models.DateField(
        null=True,   # Câmp null (3/5)
        blank=True
    )
    stare = models.CharField(
        max_length=20,
        choices=STARE_CHOICES,
        default='nou'
    )
    tags = models.CharField(
        max_length=255,
        null=True,   # Câmp null (4/5)
        blank=True,
        help_text="Etichete separate prin virgulă (ex: holo, charizard, editie-limitata)."
    )
    data_adaugare = models.DateTimeField(
        auto_now_add=True  # DateTimeField cu valoare implicită data adăugării
    )

    class Meta:
        verbose_name_plural = "Produse"
        indexes = [
            models.Index(fields=['titlu']),  # Index (3/4)
            models.Index(fields=['pret']),   # Index (4/4)
        ]
        constraints = [
            # Constrângere Q (3/5): Prețul trebuie să fie strict pozitiv
            models.CheckConstraint(
                condition=Q(pret__gt=0),
                name='check_pret_pozitiv'
            ),
            # Constrângere Q (4/5): Dacă produsul este marcat foarte rar, prețul trebuie să fie minim 50 RON
            models.CheckConstraint(
                condition=Q(este_foarte_rar=False) | Q(pret__gte=50),
                name='check_pret_minim_produs_rar'
            )
        ]

    def __str__(self):
        return f"{self.titlu} - {self.pret} RON ({self.get_stare_display()})"


class Producator(models.Model):
    nume_companie = models.CharField(
        max_length=100,
        unique=True,
        error_messages={  # Mesaje de eroare (5/5)
            'unique': "Acest producător este deja înregistrat în baza de date."
        }
    )
    tara_origine = models.CharField(max_length=60)
    website = models.URLField(
        null=True,   # Câmp null (5/5)
        blank=True
    )

    class Meta:
        verbose_name_plural = "Producători"

    def __str__(self):
        return f"{self.nume_companie} ({self.tara_origine})"


class RevistaPromotionala(models.Model):
    # Entitate slabă dependentă de Producator
    producator = models.ForeignKey(
        Producator,
        on_delete=models.CASCADE,
        related_name='reviste'
    )
    titlu_revista = models.CharField(max_length=150)
    editie_numar = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Reviste Promoționale"
        unique_together = ('producator', 'editie_numar')  # Cheie parțială + cheie părinte

    def __str__(self):
        return f"{self.titlu_revista} - Nr. {self.editie_numar} ({self.producator.nume_companie})"


class Ambalaj(models.Model):
    tip_ambalaj = models.CharField(max_length=80)
    greutate_gr = models.FloatField()

    class Meta:
        verbose_name_plural = "Ambalaje"
        constraints = [
            # Constrângere Q (5/5): Greutatea ambalajului trebuie să fie > 0 și <= 5000g
            models.CheckConstraint(
                condition=Q(greutate_gr__gt=0) & Q(greutate_gr__lte=5000),
                name='check_greutate_ambalaj_valida'
            )
        ]

    def __str__(self):
        return f"{self.tip_ambalaj} ({self.greutate_gr}g)"