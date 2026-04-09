from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="landmark_image_url",
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name="report",
            name="landmark",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
