import pytest
from graphene_django.utils.testing import graphql_query
from moxie_medspa.models import Medspa, Service, Appointment
from django.utils import timezone

def create_medspa():
    return Medspa.objects.create(
        name="Test Medspa",
        address="123 Test St",
        phone_number="555-1234",
        email_address="test@joinmoxie.com"
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

@pytest.mark.django_db
def test_create_service_mutation(client):
    medspa = create_medspa()

    response = graphql_query(
        '''
        mutation createService($name: String!, $description: String!, $price: Decimal!, $duration: Int!, $medspaId: UUID!) {
            createService(name: $name, description: $description, price: $price, duration: $duration, medspaId: $medspaId) {
                service {
                    id
                    name
                    description
                    price
                    duration
                }
            }
        }
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={
            'name': "New Service",
            'description': "New Service Description",
            'price': 200.0,
            'duration': 45,
            'medspaId': str(medspa.id)
        }
    )

    content = response.json()
    data = content['data']['createService']['service']

    assert data['name'] == "New Service"
    assert data['description'] == "New Service Description"
    assert float(data['price']) == 200.0
    assert data['duration'] == 45

    created_service = Service.objects.get(id=data['id'])
    assert created_service.name == "New Service"
    assert created_service.description == "New Service Description"
    assert created_service.price == 200.0
    assert created_service.duration == 45
    assert created_service.medspa == medspa

@pytest.mark.django_db
def test_create_appointment_mutation(client):
    medspa = create_medspa()
    service1 = create_service(medspa, name="Service A", price=100.0, duration=30)
    service2 = create_service(medspa, name="Service B", price=150.0, duration=45)

    response = graphql_query(
        '''
        mutation createAppointment($startTime: DateTime!, $serviceIds: [UUID!]!, $medspaId: UUID!) {
            createAppointment(startTime: $startTime, serviceIds: $serviceIds, medspaId: $medspaId) {
                appointment {
                    id
                    startTime
                    totalDuration
                    totalPrice
                    status
                    medspa {
                        id
                        name
                    }
                    services {
                        id
                        name
                    }
                }
            }
        }
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={
            'startTime': timezone.now().isoformat(),
            'serviceIds': [str(service1.id), str(service2.id)],
            'medspaId': str(medspa.id)
        }
    )

    content = response.json()

    if 'errors' in content:
        print("Errors:", content['errors'])

    assert 'data' in content, f"Response had no data: {content}"

    data = content['data']['createAppointment']['appointment']

    assert data['medspa']['id'] == str(medspa.id)
    assert data['totalDuration'] == service1.duration + service2.duration
    assert float(data['totalPrice']) == service1.price + service2.price
    assert len(data['services']) == 2
    assert data['status'] == 'SCHEDULED'

    assert Appointment.objects.count() == 1
    appointment = Appointment.objects.first()
    assert appointment.medspa == medspa
    assert appointment.total_duration == service1.duration + service2.duration
    assert appointment.total_price == service1.price + service2.price
    assert appointment.services.count() == 2

@pytest.mark.django_db
def test_update_service_mutation(client):
    medspa = create_medspa()
    service = create_service(medspa, name="Old Service Name", description="Old Service Description", price=100.0, duration=60)

    response = graphql_query(
        '''
        mutation updateService(
          $serviceId: UUID!,
          $name: String,
          $description: String,
          $price: Decimal,
          $duration: Int
        ) {
          updateService(
            serviceId: $serviceId,
            name: $name,
            description: $description,
            price: $price,
            duration: $duration
          ) {
            service {
              id
              name
              description
              price
              duration
            }
          }
        }
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={
            'serviceId': str(service.id),
            'name': "Updated Service Name",
            'description': "Updated Service Description",
            'price': 200.0,
            'duration': 90
        }
    )

    content = response.json()
    data = content['data']['updateService']['service']

    assert data['name'] == "Updated Service Name"
    assert data['description'] == "Updated Service Description"
    assert float(data['price']) == 200.0
    assert data['duration'] == 90

    service.refresh_from_db()
    assert service.name == "Updated Service Name"
    assert service.description == "Updated Service Description"
    assert service.price == 200.0
    assert service.duration == 90

@pytest.mark.django_db
def test_update_appointment_status_mutation(client):
    medspa = create_medspa()
    service = create_service(medspa)
    appointment = create_appointment(medspa, [service])

    response = graphql_query(
        '''
        mutation updateAppointmentStatus($appointmentId: UUID!, $status: String!) {
          updateAppointmentStatus(appointmentId: $appointmentId, status: $status) {
            appointment {
              id
              status
            }
          }
        }
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={
            'appointmentId': str(appointment.id),
            'status': "completed"
        }
    )

    content = response.json()

    if 'errors' in content:
        print("Errors:", content['errors'])

    assert 'data' in content, f"Response had no data: {content}"

    data = content['data']['updateAppointmentStatus']['appointment']

    assert data['status'] == "COMPLETED"

    appointment.refresh_from_db()
    assert appointment.status == "completed"
