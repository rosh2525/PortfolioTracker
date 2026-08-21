from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assets", "0007_settings_tax_country"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="currency",
            field=models.CharField(default="INR", max_length=3),
        ),
        migrations.AlterField(
            model_name="account",
            name="currency",
            field=models.CharField(default="INR", max_length=3),
        ),
        migrations.AlterField(
            model_name="settings",
            name="base_currency",
            field=models.CharField(default="INR", max_length=3),
        ),
        migrations.AlterField(
            model_name="settings",
            name="tax_country",
            field=models.CharField(
                default="IN",
                help_text=(
                    "User's country of fiscal residence (ISO 3166-1 alpha-2). "
                    "Drives which tax-declaration adapter is shown. "
                    "Country-specific filing adapters are optional; unsupported "
                    "countries keep the financial-analysis view."
                ),
                max_length=2,
            ),
        ),
    ]
