from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("realestate", "0002_amortization"),
    ]

    operations = [
        migrations.AlterField(
            model_name="property",
            name="currency",
            field=models.CharField(default="INR", max_length=3),
        ),
    ]
