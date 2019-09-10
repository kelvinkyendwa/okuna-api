# Generated by Django 2.2.4 on 2019-08-19 17:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_posts', '0042_postcomment_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='modified',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]