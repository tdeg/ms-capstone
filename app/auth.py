"""
Authentication helper functions.
"""
import os
import time

import jwt
from decouple import config
from google.cloud import secretmanager
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


def access_secret_version(secret_id, version_id="latest") -> str:
    """
    Access the secret.

    :secret_id: The secret id.
    :type secret_id: str
    :version_id: The version of the secret.
    :type vesion_id: str
    :return: The secret.
    :rtype: str
    """
    project_id = os.environ.get("PROJECT_ID")
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    response = client.access_secret_version(name=name)

    return response.payload.data.decode("UTF-8")


# If environmental variable "ENV" is set to "prod", grab the secrets from GCP.
# else, pull from the local .env file.
if os.environ.get("ENV") == "prod":
    JWT_SECRET = access_secret_version("JWT_SECRET", version_id="latest")
    JWT_ALGORITHM = access_secret_version("JWT_ALGORITHM", version_id="latest")
else:
    JWT_SECRET = config("SECRET")
    JWT_ALGORITHM = config("ALGORITHM")

# Create the HTTP bear authentication scheme.
security = HTTPBearer()

# Helper for hasing passwords using the bcrypt hasing algorithm,
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Computes the hash for the given password.

    :param password: The clear text password to be hashed.
    :type password: str
    :return: The hashed password.
    :rtype: str
    """
    return pwd_context.hash(password)


def verify_password(clear_text_password, hashed_password) -> bool:
    """
    Hashes the incoming clear text password, and compares it to the existing hashed password
        in the database.

    :param clear_text_password: The clear text password.
    :type clear_text_password: str
    :param hashed_password: The hashed password.
    :type hashed_password: str
    :return: True if the hashes match, false if the hashes don't match.
    :rtype: bool
    """
    return pwd_context.verify(clear_text_password, hashed_password)


def encode_token(email: str) -> str:
    """
    Creates a JSON Web Token, and encodes the user's email inside of it as the sub field.

    :param email: The user's email.
    :type email: str
    :return: The encoded JSON Web Token.
    :rtype: str
    """
    expire_time = 60 * 5  # 5 minutes
    payload = {"exp": int(time.time()) + expire_time, "iat": time.time(), "sub": email}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> str:
    """
    Decodes the JSON Web Token and returns the sub field (the user's email).

    :param token: The JSON Web Token.
    :type token: str
    :return: The encoded JSON Web Token.
    :rtype: str
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token")


def auth_wrapper(auth: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Checks the Authorization header in the incoming request for the JSON Web Token.

    :param auth: The authorization credentials.
    :type auth: HTTPAuthorizationCredentials
    :return: The decoded token.
    :rtype: str
    """
    return decode_token(auth.credentials)