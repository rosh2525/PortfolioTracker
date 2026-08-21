from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("payroll", "0006_alter_payroll_payroll_type")]

    operations = [
        migrations.AlterField(
            model_name="employer",
            name="name",
            field=models.CharField(
                help_text="Employer's legal name.",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="employer",
            name="cif",
            field=models.CharField(
                blank=True,
                help_text="Employer TAN or tax identifier (free-form).",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="employer",
            name="ss_account",
            field=models.CharField(
                blank=True,
                help_text="Employer EPFO or social-security registration number.",
                max_length=30,
            ),
        ),
    ]
