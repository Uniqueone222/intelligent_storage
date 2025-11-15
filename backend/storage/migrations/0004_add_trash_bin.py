# Generated migration for trash bin functionality

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0003_documentchunk_chunking_strategy_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediafile',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Soft delete - moved to trash'),
        ),
        migrations.AddField(
            model_name='mediafile',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='When file was moved to trash', null=True),
        ),
        migrations.AddIndex(
            model_name='mediafile',
            index=models.Index(fields=['is_deleted'], name='storage_med_is_dele_idx'),
        ),
        migrations.AddIndex(
            model_name='mediafile',
            index=models.Index(fields=['deleted_at'], name='storage_med_deleted_idx'),
        ),
    ]
