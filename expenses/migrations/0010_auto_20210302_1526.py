# Generated by Django 3.0.1 on 2021-03-02 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0009_auto_20210226_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(choices=[('BARS', 'Bar tabs'), ('ELECTRONIC', 'Electronic'), ('GROCERIES', 'Groceries'), ('MISCELLANEOUS', 'Miscellaneous')], max_length=20, null=True),
        ),
    ]
