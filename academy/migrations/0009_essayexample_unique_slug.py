from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    EssayExample = apps.get_model("academy", "EssayExample")
    used = set()
    for essay in EssayExample.objects.order_by("pk"):
        base = slugify(essay.title)[:60] or f"redacao-{essay.pk}"
        candidate = base
        suffix = 2
        while candidate in used:
            tail = f"-{suffix}"
            candidate = f"{base[:60-len(tail)]}{tail}"
            suffix += 1
        used.add(candidate)
        essay.slug = candidate
        essay.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("academy", "0008_essayexample_full_text_essayexample_slug_and_more")]

    operations = [
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="essayexample",
            name="slug",
            field=models.SlugField(max_length=60, unique=True),
        ),
    ]
