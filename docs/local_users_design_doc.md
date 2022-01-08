# Overview 

This document covers the design elements of a local user accounts for BOE.

## Models

LocalCredentialModel
- Properties
  - username
    - type: str
  - password_hash
    - type: bytes 
    - constraints
      - encoded using simple base64
  - token

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