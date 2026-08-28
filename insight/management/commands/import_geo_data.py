import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from insight.models import State, LGA, Ward, PollingUnit

class Command(BaseCommand):
    help = 'Imports hierarchical geographic data (State, LGA, Ward, Polling Unit) from a GeoJSON file.'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file', type=str, help='Path to the GeoJSON file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['geojson_file']
        self.stdout.write(self.style.SUCCESS(f'Reading data from {file_path}...'))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Invalid JSON file.'))
            return

        if data.get('type') != 'FeatureCollection':
            self.stdout.write(self.style.ERROR('Invalid GeoJSON: Must be a FeatureCollection'))
            return

        stats = {'State': 0, 'LGA': 0, 'Ward': 0, 'PollingUnit': 0, 'Skipped': 0}

        for feature in data['features']:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry')
            
            if not geometry:
                stats['Skipped'] += 1
                continue

            # Flexible property extraction
            name = properties.get('NAME') or properties.get('name') or properties.get('LGA_NAME') or 'Unknown'
            
            # Determine the geographic tier
            geo_type_raw = properties.get('TYPE') or properties.get('type') or properties.get('TIER') or ''
            geo_type = geo_type_raw.upper().strip()
            
            # Normalize common terms
            if 'LOCAL GOVERNMENT' in geo_type or geo_type == 'LGA':
                geo_type = 'LGA'
            elif 'WARD' in geo_type or geo_type == 'REGISTRATION AREA':
                geo_type = 'WARD'
            elif 'POLLING' in geo_type or geo_type == 'PU':
                geo_type = 'POLLING_UNIT'
            elif 'STATE' in geo_type:
                geo_type = 'STATE'
            else:
                # Fallback: If it has a STATE property, assume it's an LGA for that state
                if properties.get('STATE') or properties.get('STATE_NAME'):
                    geo_type = 'LGA'
                else:
                    geo_type = 'UNKNOWN'

            if name == 'Unknown' or geo_type == 'UNKNOWN':
                stats['Skipped'] += 1
                continue

            # Convert geometry to PostGIS format
            try:
                geos_geom = GEOSGeometry(json.dumps(geometry), srid=4326)
                if geos_geom.geom_type == 'Polygon':
                    geos_geom = MultiPolygon(geos_geom)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Invalid geometry for {name}: {e}'))
                stats['Skipped'] += 1
                continue

            # --- HIERARCHICAL UPSERT LOGIC ---
            try:
                if geo_type == 'STATE':
                    obj, created = State.objects.get_or_create(
                        name=name, 
                        defaults={'code': properties.get('CODE') or name[:2].upper(), 'boundary': geos_geom}
                    )
                elif geo_type == 'LGA':
                    state_name = properties.get('STATE') or properties.get('STATE_NAME') or 'Taraba'
                    state, _ = State.objects.get_or_create(name=state_name, defaults={'code': 'TR'})
                    obj, created = LGA.objects.get_or_create(
                        name=name, 
                        state=state, 
                        defaults={'boundary': geos_geom}
                    )
                elif geo_type == 'WARD':
                    lga_name = properties.get('LGA') or properties.get('LGA_NAME') or 'Jalingo'
                    state, _ = State.objects.get_or_create(name='Taraba', defaults={'code': 'TR'})
                    lga, _ = LGA.objects.get_or_create(name=lga_name, state=state)
                    obj, created = Ward.objects.get_or_create(
                        name=name, lga=lga, defaults={'boundary': geos_geom}
                    )
                elif geo_type == 'POLLING_UNIT':
                    ward_name = properties.get('WARD') or properties.get('WARD_NAME') or 'Wukari Central'
                    lga_name = properties.get('LGA') or properties.get('LGA_NAME') or 'Wukari'
                    state, _ = State.objects.get_or_create(name='Taraba', defaults={'code': 'TR'})
                    lga, _ = LGA.objects.get_or_create(name=lga_name, state=state)
                    ward, _ = Ward.objects.get_or_create(name=ward_name, lga=lga)
                    
                    if geos_geom.geom_type in ['MultiPoint', 'Point']:
                        obj, created = PollingUnit.objects.get_or_create(
                            name=name, ward=ward, 
                            defaults={'location': geos_geom, 'boundary': None}
                        )
                    else:
                        obj, created = PollingUnit.objects.get_or_create(
                            name=name, ward=ward, 
                            defaults={'boundary': geos_geom, 'location': geos_geom.centroid}
                        )
                else:
                    stats['Skipped'] += 1
                    continue

                if created:
                    stats[geo_type] = stats.get(geo_type, 0) + 1
                    self.stdout.write(self.style.SUCCESS(f'  [+] Created {geo_type}: {name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [~] Already exists: {name}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error saving {name}: {e}'))
                stats['Skipped'] += 1

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*40))
        self.stdout.write(self.style.SUCCESS('IMPORT SUMMARY'))
        self.stdout.write(self.style.SUCCESS(f"States created:        {stats.get('State', 0)}"))
        self.stdout.write(self.style.SUCCESS(f"LGAs created:          {stats.get('LGA', 0)}"))
        self.stdout.write(self.style.SUCCESS(f"Wards created:         {stats.get('Ward', 0)}"))
        self.stdout.write(self.style.SUCCESS(f"Polling Units created: {stats.get('PollingUnit', 0)}"))
        self.stdout.write(self.style.WARNING(f"Skipped/Errors:        {stats.get('Skipped', 0)}"))
        self.stdout.write(self.style.SUCCESS('='*40))