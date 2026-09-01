from django.db import migrations

def fill_ai_nulls(apps, schema_editor):
    # Get the historical version of the Report model
    Report = apps.get_model('insight', 'Report')
    
    # Safely update all NULL values to empty strings so the next migration can run
    Report.objects.filter(ai_suggested_category__isnull=True).update(ai_suggested_category='')
    Report.objects.filter(ai_sentiment__isnull=True).update(ai_sentiment='')
    Report.objects.filter(ai_urgency_level__isnull=True).update(ai_urgency_level='')

class Migration(migrations.Migration):

    dependencies = [
        ('insight', '0004a_fill_ai_nulls'),
    ]

    operations = [
        migrations.RunPython(fill_ai_nulls),
    ]