from django.core.management.base import BaseCommand
from insight.models import LGA

class Command(BaseCommand):
    help = 'Seeds Delta State LGAs into the database'

    def handle(self, *args, **kwargs):
        delta_lgas = [
            ('Asaba', 'DELTA'), ('Warri', 'DELTA'), ('Sapele', 'DELTA'),
            ('Ughelli', 'DELTA'), ('Agbor', 'DELTA'), ('Kwale', 'DELTA'),
            ('Ogwashi-Uku', 'DELTA'), ('Abraka', 'DELTA'), ('Koko', 'DELTA'),
            ('Isoko', 'DELTA'), ('Ozoro', 'DELTA'), ('Patani', 'DELTA'),
            ('Burutu', 'DELTA'), ('Bomadi', 'DELTA'), ('Effurun', 'DELTA'),
            ('Ukwuani', 'DELTA'), ('Akuku', 'DELTA'), ('Onicha-Ugbo', 'DELTA'),
            ('Idumuje-Ugboko', 'DELTA'), ('Abbi', 'DELTA'), ('Ogor', 'DELTA'),
            ('Ogidigben', 'DELTA'), ('Otor-Udu', 'DELTA'), ('Udu', 'DELTA'),
            ('Orerokpe', 'DELTA'),
        ]

        created_count = 0
        for name, state in delta_lgas:
            obj, created = LGA.objects.get_or_create(
                name=name,
                state=state,
                defaults={'population': 0} # Boundary can be added later via GeoJSON
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} new Delta State LGAs!'))