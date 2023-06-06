# Generated by Django 3.2.18 on 2023-06-02 09:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mountains.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mountains', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, upload_to=mountains.models.Review.image_path)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', models.CharField(max_length=200)),
            ],
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'managed': False, 'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='coursedetail',
            options={'managed': False, 'ordering': ['id']},
        ),
        migrations.AlterModelTable(
            name='course',
            table='mountains_course',
        ),
        migrations.AlterModelTable(
            name='coursedetail',
            table='mountains_coursedetail',
        ),
        migrations.AlterModelTable(
            name='mountain',
            table='mountains_mountain',
        ),
        migrations.AddField(
            model_name='review',
            name='mountain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mountains.mountain'),
        ),
        migrations.AddField(
            model_name='review',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
