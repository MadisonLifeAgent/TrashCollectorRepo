# Generated by Django 3.2.5 on 2021-08-03 15:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_completedpickup'),
    ]

    operations = [
        migrations.CreateModel(
            name='Special_pickups',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(editable=False)),
                ('customer', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='customers.customer')),
            ],
        ),
    ]