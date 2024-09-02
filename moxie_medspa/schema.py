import graphene
from graphene_django.types import DjangoObjectType
from moxie_medspa.models import Medspa, Service, Appointment

class MedspaType(DjangoObjectType):
    class Meta:
        model = Medspa
        fields = '__all__'

class ServiceType(DjangoObjectType):
    class Meta:
        model = Service
        fields = '__all__'

class AppointmentType(DjangoObjectType):
    class Meta:
        model = Appointment
        fields = '__all__'

class Query(graphene.ObjectType):
    medspa = graphene.Field(MedspaType, id=graphene.UUID())
    all_medspas = graphene.List(MedspaType)

    service = graphene.Field(ServiceType, id=graphene.UUID())
    all_services = graphene.List(ServiceType, medspa_id=graphene.UUID())

    appointment = graphene.Field(AppointmentType, id=graphene.UUID())
    all_appointments = graphene.List(AppointmentType, status=graphene.String(), start_date=graphene.Date())

    appointments_by_medspa = graphene.List(AppointmentType, medspa_id=graphene.UUID(), date=graphene.Date())

    def resolve_medspa(self, info, id):
        return Medspa.objects.get(pk=id)

    def resolve_all_medspas(self, info):
        return Medspa.objects.all()

    def resolve_service(self, info, id):
        return Service.objects.get(pk=id)

    def resolve_all_services(self, info, medspa_id=None):
        if medspa_id:
            return Service.objects.filter(medspa__id=medspa_id)
        return Service.objects.all()

    def resolve_appointment(self, info, id):
        return Appointment.objects.get(pk=id)

    def resolve_all_appointments(self, info, status=None, start_date=None):
        query = Appointment.objects.all()
        if status:
            query = query.filter(status=status)
        if start_date:
            query = query.filter(start_time__date=start_date)
        return query

    def resolve_appointments_by_medspa(self, info, medspa_id, date=None):
        query = Appointment.objects.filter(medspa__id=medspa_id)
        if date:
            query = query.filter(start_time__date=date)
        return query

class CreateService(graphene.Mutation):
    service = graphene.Field(ServiceType)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        duration = graphene.Int(required=True)
        medspa_id = graphene.UUID(required=True)

    def mutate(self, info, name, description, price, duration, medspa_id):
        medspa = Medspa.objects.get(id=medspa_id)
        service = Service(name=name, description=description, price=price, duration=duration, medspa=medspa)
        service.save()
        return CreateService(service=service)

class CreateAppointment(graphene.Mutation):
    appointment = graphene.Field(AppointmentType)

    class Arguments:
        start_time = graphene.DateTime(required=True)
        service_ids = graphene.List(graphene.UUID, required=True)
        medspa_id = graphene.UUID(required=True)

    def mutate(self, info, start_time, service_ids, medspa_id):
        medspa = Medspa.objects.get(id=medspa_id)
        services = Service.objects.filter(id__in=service_ids)

        total_duration = sum(service.duration for service in services)
        total_price = sum(service.price for service in services)

        appointment = Appointment(
            start_time=start_time,
            total_duration=total_duration,
            total_price=total_price,
            status='scheduled', # set the default status
            medspa=medspa
        )
        appointment.save()
        appointment.services.set(services)

        return CreateAppointment(appointment=appointment)

class UpdateService(graphene.Mutation):
    service = graphene.Field(ServiceType)

    class Arguments:
        service_id = graphene.UUID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        price = graphene.Decimal(required=False)
        duration = graphene.Int(required=False)

    def mutate(self, info, service_id, name=None, description=None, price=None, duration=None):
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            raise Exception('Service not found')

        if name:
            service.name = name
        if description:
            service.description = description
        if price:
            service.price = price
        if duration:
            service.duration = duration

        service.save()
        return UpdateService(service=service)

class UpdateAppointmentStatus(graphene.Mutation):
    appointment = graphene.Field(AppointmentType)

    class Arguments:
        appointment_id = graphene.UUID(required=True)
        status = graphene.String(required=True)

    def mutate(self, info, appointment_id, status):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            raise Exception('Appointment not found')

        valid_statuses = ['scheduled', 'completed', 'canceled']
        if status not in valid_statuses:
            raise Exception(f"Invalid status. Expected one of {valid_statuses}")

        appointment.status = status
        appointment.save()

        return UpdateAppointmentStatus(appointment=appointment)

class Mutation(graphene.ObjectType):
    create_service = CreateService.Field()
    update_service = UpdateService.Field()
    create_appointment = CreateAppointment.Field()
    update_appointment_status = UpdateAppointmentStatus.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

