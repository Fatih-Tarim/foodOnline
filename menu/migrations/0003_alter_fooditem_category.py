# Generated by Django 4.2.7 on 2023-12-25 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0002_alter_category_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fooditem",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="fooditems",
                to="menu.category",
            ),
        ),
    ]
