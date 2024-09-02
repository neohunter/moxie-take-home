import pytest
from graphene_django.utils.testing import graphql_query
from moxie_medspa.models import Medspa, Service, Appointment
from django.utils import timezone
from moxie_medspa.tests.test_helpers import create_medspa, create_service, create_appointment, execute_graphql_query

@pytest.mark.django_db
def test_query_all_medspas(client):
    test_medspa = create_medspa()

    content = execute_graphql_query(
        client,
        '''
        query {
            allMedspas {
                id
                name
                address
            }
        }
        '''
    )

    data = content['data']['allMedspas']
    assert len(data) == Medspa.objects.count()
    assert data[-1]['name'] == test_medspa.name
    assert data[-1]['address'] == test_medspa.address
    assert data[-1]['id'] == str(test_medspa.id)

@pytest.mark.django_db
def test_query_service_by_medspa(client):
    medspa = create_medspa()
    service = create_service(medspa)

    content = execute_graphql_query(
        client,
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
        variables={'medspaId': str(medspa.id)}
    )

    data = content['data']['allServices']
    assert len(data) == 1
    assert data[0]['name'] == service.name
    assert data[0]['description'] == service.description
    assert data[0]['id'] == str(service.id)

@pytest.mark.django_db
def test_query_specific_medspa(client):
    test_medspa = create_medspa(name="Specific Medspa", address="456 Test Rd", phone_number="555-5678", email_address="specific@joinmoxie.com")

    content = execute_graphql_query(
        client,
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
        variables={'id': str(test_medspa.id)}
    )

    data = content['data']['medspa']
    assert data['name'] == test_medspa.name
    assert data['address'] == test_medspa.address
    assert data['phoneNumber'] == test_medspa.phone_number
    assert data['emailAddress'] == test_medspa.email_address
    assert data['id'] == str(test_medspa.id)

@pytest.mark.django_db
def test_query_specific_service(client):
    medspa = create_medspa(name="Medspa for Service", address="789 Service St", phone_number="555-7890", email_address="service@joinmoxie.com")
    test_service = create_service(medspa, name="Specific Service", description="A specific service description", price=300.0, duration=60)

    content = execute_graphql_query(
        client,
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
        variables={'id': str(test_service.id)}
    )

    data = content['data']['service']
    assert data['name'] == test_service.name
    assert data['description'] == test_service.description
    assert float(data['price']) == test_service.price
    assert data['duration'] == test_service.duration
    assert data['medspa']['id'] == str(medspa.id)
    assert data['medspa']['name'] == medspa.name

@pytest.mark.django_db
def test_query_specific_appointment(client):
    medspa = create_medspa(name="Medspa for Appointment", address="123 Appointment St", phone_number="555-1010", email_address="appointment@joinmoxie.com")
    service = create_service(medspa, name="Appointment Service", description="A service for appointments", price=150.0, duration=30)
    test_appointment = create_appointment(medspa, [service])

    content = execute_graphql_query(
        client,
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
        variables={'id': str(test_appointment.id)}
    )

    data = content['data']['appointment']
    assert data['id'] == str(test_appointment.id)
    assert data['status'] == test_appointment.status.upper()
    assert float(data['totalPrice']) == test_appointment.total_price
    assert data['totalDuration'] == test_appointment.total_duration
    assert data['medspa']['id'] == str(medspa.id)
    assert data['medspa']['name'] == medspa.name
    assert len(data['services']) == 1
    assert data['services'][0]['id'] == str(service.id)
    assert data['services'][0]['name'] == service.name

@pytest.mark.django_db
def test_query_appointments_by_medspa(client):
    medspa = create_medspa(name="Medspa for Appointments", address="123 Appointments St", phone_number="555-1212", email_address="appointments@joinmoxie.com")
    service1 = create_service(medspa, name="Service A", price=100.0, duration=30)
    service2 = create_service(medspa, name="Service B", price=150.0, duration=45)

    create_appointment(medspa, [service1])
    create_appointment(medspa, [service2], start_time=timezone.now() - timezone.timedelta(days=1), status='completed')

    content = execute_graphql_query(
        client,
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
        variables={'medspaId': str(medspa.id)}
    )

    data = content['data']['appointmentsByMedspa']
    assert len(data) == 2
    assert data[0]['medspa']['id'] == str(medspa.id)
    assert data[0]['medspa']['name'] == medspa.name

    content = execute_graphql_query(
        client,
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
        variables={
            'medspaId': str(medspa.id),
            'date': timezone.now().date().isoformat()
        }
    )

    data = content['data']['appointmentsByMedspa']
    assert len(data) == 1
    assert data[0]['medspa']['id'] == str(medspa.id)
    assert data[0]['medspa']['name'] == medspa.name
    assert data[0]['status'] == 'SCHEDULED'
