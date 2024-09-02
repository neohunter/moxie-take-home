import pytest
from graphene_django.utils.testing import graphql_query
from moxie_medspa.models import Medspa, Service, Appointment
from django.utils import timezone

@pytest.mark.django_db
def test_query_all_medspas(client):
    test_medspa = Medspa.objects.create(
        name="Test Medspa",
        address="123 Test St",
        phone_number="555-1234",
        email_address="test@joinmoxie.com"
    )

    response = graphql_query(
        '''
        query {
            allMedspas {
                id
                name
                address
            }
        }
        ''',
        client=client,
        graphql_url="/graphql/"
    )

    content = response.json()
    data = content['data']['allMedspas']

    assert len(data) == Medspa.objects.count()

    assert data[-1]['name'] == test_medspa.name
    assert data[-1]['address'] == test_medspa.address
    assert data[-1]['id'] == str(test_medspa.id)

@pytest.mark.django_db
def test_query_service_by_medspa(client):
    medspa = Medspa.objects.create(name="Test Medspa", address="123 Test St", phone_number="555-1234", email_address="test@joinmoxie.com")
    service = Service.objects.create(
        name="Test Service",
        description="A test service",
        price=100.0,
        duration=60,
        medspa=medspa
    )

    response = graphql_query(
        '''
        query($medspaId: UUID!) {
            allServices(medspaId: $medspaId) {
                id
                name
                description
                price
            }
        }
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={'medspaId': str(medspa.id)}
    )

    content = response.json()
    data = content['data']['allServices']

    assert len(data) == 1

    assert data[0]['name'] == service.name
    assert data[0]['description'] == service.description
    assert data[0]['id'] == str(service.id)



@pytest.mark.django_db
def test_query_specific_medspa(client):
    test_medspa = Medspa.objects.create(
        name="Specific Medspa",
        address="456 Test Rd",
        phone_number="555-5678",
        email_address="specific@joinmoxie.com"
    )

    response = graphql_query(
        '''
        query getMedspa($id: UUID!) {
            medspa(id: $id) {
                id
                name
                address
                phoneNumber
                emailAddress
            }
        }
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={'id': str(test_medspa.id)}
    )

    content = response.json()
    data = content['data']['medspa']

    assert data['name'] == test_medspa.name
    assert data['address'] == test_medspa.address
    assert data['phoneNumber'] == test_medspa.phone_number
    assert data['emailAddress'] == test_medspa.email_address
    assert data['id'] == str(test_medspa.id)

@pytest.mark.django_db
def test_query_specific_service(client):
    medspa = Medspa.objects.create(
        name="Medspa for Service",
        address="789 Service St",
        phone_number="555-7890",
        email_address="service@joinmoxie.com"
    )
    test_service = Service.objects.create(
        name="Specific Service",
        description="A specific service description",
        price=300.0,
        duration=60,
        medspa=medspa
    )

    response = graphql_query(
        '''
        query getService($id: UUID!) {
            service(id: $id) {
                id
                name
                description
                price
                duration
                medspa {
                    id
                    name
                }
            }
        }
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={'id': str(test_service.id)}
    )

    content = response.json()
    data = content['data']['service']

    assert data['name'] == test_service.name
    assert data['description'] == test_service.description
    assert float(data['price']) == test_service.price
    assert data['duration'] == test_service.duration
    assert data['medspa']['id'] == str(medspa.id)
    assert data['medspa']['name'] == medspa.name

@pytest.mark.django_db
def test_query_specific_appointment(client):
    medspa = Medspa.objects.create(
        name="Medspa for Appointment",
        address="123 Appointment St",
        phone_number="555-1010",
        email_address="appointment@joinmoxie.com"
    )
    service = Service.objects.create(
        name="Appointment Service",
        description="A service for appointments",
        price=150.0,
        duration=30,
        medspa=medspa
    )
    test_appointment = Appointment.objects.create(
        start_time=timezone.now(),
        total_duration=service.duration,
        total_price=service.price,
        status='SCHEDULED',
        medspa=medspa
    )
    test_appointment.services.add(service)

    response = graphql_query(
        '''
        query getAppointment($id: UUID!) {
            appointment(id: $id) {
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
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={'id': str(test_appointment.id)}
    )

    content = response.json()
    data = content['data']['appointment']

    assert data['id'] == str(test_appointment.id)
    assert data['status'] == test_appointment.status
    assert float(data['totalPrice']) == test_appointment.total_price
    assert data['totalDuration'] == test_appointment.total_duration
    assert data['medspa']['id'] == str(medspa.id)
    assert data['medspa']['name'] == medspa.name
    assert len(data['services']) == 1
    assert data['services'][0]['id'] == str(service.id)
    assert data['services'][0]['name'] == service.name

@pytest.mark.django_db
def test_query_appointments_by_medspa(client):
    medspa = Medspa.objects.create(
        name="Medspa for Appointments",
        address="123 Appointments St",
        phone_number="555-1212",
        email_address="appointments@joinmoxie.com"
    )
    service1 = Service.objects.create(
        name="Service A",
        description="Service A Description",
        price=100.0,
        duration=30,
        medspa=medspa
    )
    service2 = Service.objects.create(
        name="Service B",
        description="Service B Description",
        price=150.0,
        duration=45,
        medspa=medspa
    )

    appointment1 = Appointment.objects.create(
        start_time=timezone.now(),
        total_duration=service1.duration,
        total_price=service1.price,
        status='scheduled',
        medspa=medspa
    )
    appointment1.services.add(service1)

    appointment2 = Appointment.objects.create(
        start_time=timezone.now() - timezone.timedelta(days=1),
        total_duration=service2.duration,
        total_price=service2.price,
        status='completed',
        medspa=medspa
    )
    appointment2.services.add(service2)

    response = graphql_query(
        '''
        query getAppointmentsByMedspa($medspaId: UUID!) {
            appointmentsByMedspa(medspaId: $medspaId) {
                id
                startTime
                status
                medspa {
                    id
                    name
                }
            }
        }
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={'medspaId': str(medspa.id)}
    )

    content = response.json()
    print(content)
    data = content['data']['appointmentsByMedspa']

    assert len(data) == 2
    assert data[0]['medspa']['id'] == str(medspa.id)
    assert data[0]['medspa']['name'] == medspa.name

    response = graphql_query(
        '''
        query getAppointmentsByMedspa($medspaId: UUID!, $date: Date) {
            appointmentsByMedspa(medspaId: $medspaId, date: $date) {
                id
                startTime
                status
                medspa {
                    id
                    name
                }
            }
        }
        ''',
        client=client,
        graphql_url="/graphql/",
        variables={
            'medspaId': str(medspa.id),
            'date': timezone.now().date().isoformat()
        }
    )

    content = response.json()
    data = content['data']['appointmentsByMedspa']

    assert len(data) == 1
    assert data[0]['medspa']['id'] == str(medspa.id)
    assert data[0]['medspa']['name'] == medspa.name
    assert data[0]['status'] == 'SCHEDULED'
