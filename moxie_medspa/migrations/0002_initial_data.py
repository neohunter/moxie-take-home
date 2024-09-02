from django.db import migrations

def create_initial_data(apps, schema_editor):
    Medspa = apps.get_model('moxie_medspa', 'Medspa')
    Service = apps.get_model('moxie_medspa', 'Service')

    medspas = [
        {
            "name": "Lux Aesthetics",
            "address": "123 Main St",
            "phone_number": "310-555-1234",
            "email_address": "info@joinmoxie.com"
        },
        {
            "name": "Elite MedSpa",
            "address": "456 Elm St",
            "phone_number": "212-555-1234",
            "email_address": "info@joinmoxie.com"
        },
        {
            "name": "Rejuvenate Clinic",
            "address": "123 Main St",
            "phone_number": "305-555-1234",
            "email_address": "info@joinmoxie.com"
        },
    ]

    services = [
        {
            "name": "Botox Injection",
            "description": "Reduces wrinkles and fine lines.",
            "price": 200.0,
            "duration": 30
        },
        {
            "name": "Dermal Filler",
            "description": "Restores volume and fullness to the face.",
            "price": 400.0,
            "duration": 45
        },
        {
            "name": "Laser Hair Removal",
            "description": "Removes unwanted hair permanently.",
            "price": 150.0,
            "duration": 60
        },
    ]


    for medspa_data in medspas:
        medspa = Medspa.objects.create(**medspa_data)
        for service_data in services:
            Service.objects.create(medspa=medspa, **service_data)


class Migration(migrations.Migration):

    dependencies = [
        ('moxie_medspa', '0001_initial'),  # Reemplaza con el nombre de la migración inicial
    ]

    operations = [
        migrations.RunPython(create_initial_data),
    ]
