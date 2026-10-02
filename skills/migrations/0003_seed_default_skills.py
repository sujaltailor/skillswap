from django.db import migrations


DEFAULT_SKILLS = (
    "HTML",
    "DJANGO",
    "CSS",
    "Python",
    "JavaScript",
    "Photoshop",
)


def create_default_skills(apps, schema_editor):
    Skill = apps.get_model("skills", "Skill")
    database = schema_editor.connection.alias

    for name in DEFAULT_SKILLS:
        Skill.objects.using(database).get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [
        ("skills", "0002_exchangerequest"),
    ]

    operations = [
        migrations.RunPython(create_default_skills, migrations.RunPython.noop),
    ]