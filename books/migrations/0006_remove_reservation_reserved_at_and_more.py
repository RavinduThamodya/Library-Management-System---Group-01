# Generated by Django 5.2 on 2025-04-26 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0005_book_copies_book_total_copies_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="reservation",
            name="reserved_at",
        ),
        migrations.RemoveField(
            model_name="reservation",
            name="reserved_date",
        ),
    ]
