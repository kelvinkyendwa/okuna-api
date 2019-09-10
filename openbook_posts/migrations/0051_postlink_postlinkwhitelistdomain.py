# Generated by Django 2.2.4 on 2019-08-24 19:52

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_posts', '0050_auto_20190823_1259'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostLinkWhitelistDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=126)),
            ],
        ),
        migrations.CreateModel(
            name='PostLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('link', models.CharField(max_length=5000)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_links', to='openbook_posts.Post')),
            ],
            options={
                'unique_together': {('post', 'link')},
            },
        ),
    ]