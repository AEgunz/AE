from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0021_productrating'),  # هذا هو آخر migration عندك
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2),
        ),
    ]