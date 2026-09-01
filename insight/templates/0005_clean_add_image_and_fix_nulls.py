from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('insight', '0004_remove_fieldagent_created_at_and_more'),
    ]

    operations = [
        # 1. Add the new image field
        migrations.AddField(
            model_name='report',
            name='image_base64',
            field=models.TextField(blank=True, help_text='Base64 encoded image from mobile app', null=True),
        ),
        # 2. Fix the AI fields to allow NULLs safely
        migrations.AlterField(
            model_name='report',
            name='ai_suggested_category',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='ai_confidence_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='ai_sentiment',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='ai_urgency_level',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='ai_extracted_entities',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]