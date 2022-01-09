# Overview 

This document covers the design elements of a local user accounts for BOE.

## Models

### API 
FamilyRegistrationRequest
- properties
  - family_name
  - first_name
  - last_name
  - email
  - dob
    - type: datetime 
    - constraints
      - Format="1988-09-06T00:00:00"

### User Domain:

LocalCredentialModel
- Properties
  - username
    - type: str
  - password_hash
    - type: bytes 
    - constraints
      - encoded using base64
  - token
    - type: bytes
    - constraints
      - encoded using base64

UserAccountAggregate
- properties
  - creds

## Domain Events

Related Domains and events 
- Store Domain
  - CreateFamilyStoreEvent

- User Domain
  - CreateFamilyEvent
  - CreateAdultAccountEvent
  - CreateLocalCredentialsEvent


## Application Events