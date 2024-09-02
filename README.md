# moxie-take-home
Moxie Take home assesment for Arnold M. Roa

Dear Technical Recruiter,

I sincerely appreciate you taking the time to review this project, which has been completed
as part of the take-home assessment for the Lead Backend Engineer Python position.

I have organized the core entities, such as MedSpa, Services, and Appointments.
However, this API currently does not include an authentication system or a user
table to link appointments to individuals. Additionally, it lacks validation
mechanisms for mutations, such as preventing unintended modifications to certain fields,
or validating data.

While this is not a fully comprehensive solution, I believe it provides a solid
glimpse into my backend development capabilities and my strategic approach to application
architecture design of which are essential for leading technical teams, developing new
product features, and optimizing or refactoring systems to deliver value to the
organization.

I chose to implement GraphQL for this project as I understand it is the backend
technology used for the API at Moxie, along with Hasura.io. This implementation
includes the primary queries and mutations.

A basic set of tests for the GraphQL queries is also included.

I created a simple docker environment to be able to test this without having to
worry about the setup.

I hope you enjoy it!

Sincerely yous,

Arnold M. Roa

Being said that, lets dive in!

# Moxie Medspa API

Moxie Medspa API is a sample GraphQL-based application designed to manage medspas, their services,
and appointments through a set of GraphQL queries and mutations. This project is built with Django,
PostgreSQL,  Docker and GraphQL and of course...  it's not suppose to be used in production... yet ;)

Here's a brief overview of the functionality:

1. **Medspas**: You can create and manage multiple medspas, each with its own unique name, address,
phone number, and email address.

2. **Services**: Each medspa can offer multiple services, Services have attributes like name, description,
price, and duration.

3. **Appointments**: Clients can book appointments at medspas, selecting one or more services. The API calculates
the total duration and price of the appointment based on the selected services. We need to define where clients
are going to be stored, and decide if we want some kind of authorization.


## Setup

To set up the application, ensure that you have Docker installed. Then follow these steps:

```bash
$ docker compose build
$ docker compose up
```

It will take care of create the database and insert some sample data.

# Testing endpoints

Once the application is running, you can access the GraphiQL interface at:

(http://localhost:8000/graphql/)[http://localhost:8000/graphql/]

From here, you can run queries and mutations to interact with the API. For example, you can query all medspas, create new services, or book appointments.


## GraphQL queries

Here you can find some references for the implemented queries and mutations.

```graphql
# List all Medspas
# ---------------------------

query {
  allMedspas {
    id
    name
    address
    phoneNumber
    emailAddress
  }
}

# List all Services for a specific Medspa
# --------------------------------------------------
# use the variables section to set `medspaId` with the ID of the medspa you want to query.
#  ie: {"medspaId": "aec71f83-346d-4e73-9d27-72ca00c3ff78"}

query getServices($medspaId: UUID!) {
  allServices(medspaId: $medspaId) {
    id
    name
    description
    price
    duration
  }
}

# List all Appointments
# --------------------------------

query {
  allAppointments {
    id
    startTime
    totalDuration
    totalPrice
    status
    medspa {
      id
      name
    }
  }
}

# List all appointments by medspa, filtering by date
# -------------------------------
# example variables:
  {
    "date": "2024-08-31",
    "medspaId": "aec71f83-346d-4e73-9d27-72ca00c3ff78"
  }

query getAppointmentsByMedspa($medspaId: UUID!, $date: Date) {
  appointmentsByMedspa(medspaId: $medspaId, date: $date) {
    id
    startTime
    status
    totalDuration
    totalPrice
    medspa {
      id
      name
    }
  }
}

# Create a new Service
# -------------------------------

mutation createService(
  $name: String!,
  $description: String!,
  $price: Decimal!,
  $duration: Int!,
  $medspaId: UUID!
) {
  createService(
    name: $name,
    description: $description,
    price: $price,
    duration: $duration,
    medspaId: $medspaId
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

# Create a new Appointment
# -----------------------------------
# example variables:
  {
    "startTime": "2024-08-31T15:00:00Z",
    "serviceIds": ["b2a5f614-ff12-4a8b-8a2b-c7a8ffed8b91", "aec71f83-346d-4e73-9d27-72ca00c3ff78"],
    "medspaId": "aec71f83-346d-4e73-9d27-72ca00c3ff78"
  }

mutation createAppointment(
  $startTime: DateTime!,
  $serviceIds: [UUID!]!,
  $medspaId: UUID!
) {
  createAppointment(
    startTime: $startTime,
    serviceIds: $serviceIds,
    medspaId: $medspaId
  ) {
    appointment {
      id
      startTime
      totalDuration
      totalPrice
      status
      services {
        id
        name
      }
      medspa {
        id
        name
      }
    }
  }
}
```

# Run tests
You can run the tests using the following command:

```bash
$ docker-compose run web pytest
```

# Tasks
- [X] Auto create db files on build
- [X] Filter appointments by medSpa, by data range
- [X] Endpoints to get Medspa, services, and all appointments
- [X] Endpoint to get all appointments by medSpa, filtering by date
- [X] Write tests
- [] Auth
- [] Validate that the services passed in createApointment belongs to the medSpa
