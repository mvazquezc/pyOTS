# Python One Time Secret
> Provides an API to interact with OTS

> This project has started as a way to improve my Python knowledge, so expect bad practices and buggy software. 

> I look forward to hearing possible improvements in the software as well as PR.

## Project Description
pyOTS is created on top of Flask, it provides enpoints to interact with One Time Secrets.

## TODO
* Improve security
* Provide a WUI
* Provide a way to auto-remove expired secrets from the database
* Send secrets via email (?)


## Features
* Create a secret (with/out password)
* Open a secret
* Delete a secret
* Generate a random password

## Endpoints:

| Endpoint                                  | VERB   | Description                                  |
|-------------------------------------------|--------|----------------------------------------------|
| /view/<token>                             | GET    | Shows information about the secret           |
| /open                                     | POST   | Opens a secret based on the json data sent   |
| /create                                   | POST   | Creates a secret based on the json data sent |
| /delete/<token>                           | DELETE | Deletes a given secret                       |
| /random-password                          | GET    | Returns a randomly generated password        |

## Examples:
TBD