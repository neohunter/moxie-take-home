from moxie_medspa.models import Medspa, Service, Appointment
from django.utils import timezone

def create_medspa(name="Test Medspa", address="123 Test St", phone_number="555-1234", email_address="test@joinmoxie.com"):
    return Medspa.objects.create(
        name=name,
        address=address,
        phone_number=phone_number,
        email_address=email_address
    )

def create_service(medspa, name="Test Service", description="Test Service Description", price=100.0, duration=60):
    return Service.objects.create(
        name=name,
        description=description,
        price=price,
        duration=duration,
        medspa=medspa
    )

def create_appointment(medspa, services, start_time=None, status='scheduled'):
    appointment = Appointment.objects.create(
        start_time=start_time or timezone.now(),
        total_duration=sum(service.duration for service in services),
        total_price=sum(service.price for service in services),
        status=status,
        medspa=medspa
    )
    appointment.services.set(services)
    return appointment

def execute_graphql_query(client, query, variables=None):
    return client.post('/graphql/', {'query': query, 'variables': variables}, content_type='application/json').json()
