# Generated by Django 4.1.1 on 2024-04-23 17:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_addr'),
    ]

    operations = [
        migrations.AddField(
            model_name='addr',
            name='balance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.balance'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='addr',
            name='address',
        ),
        migrations.AddField(
            model_name='addr',
            name='address',
            field=models.CharField(max_length=250),
            preserve_default=False,
        ),
    ]