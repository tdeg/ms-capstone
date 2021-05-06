"""
The API routes for our Application.
"""
from fastapi import FastAPI, Body, Depends
from fastapi.responses import JSONResponse

from app.schemas import User, Message
from app.auth import get_password_hash, verify_password, encode_token, auth_wrapper


# Instantiate a FastAPI object
app = FastAPI()

# Create an in memory database using a list
database = []

# Create an in memory database using a list
messages = []


def check_user(incoming_user: User) -> bool:
    """
    Check to see if the user's credentials match what we have in our database.

    :param incoming_user: The JSON body from the incoming request.
    :type incoming_user: User
    :return: Whether the user logged in successfully or not.
    :rtype: bool
    """
    for user in database:
        if user.email == incoming_user.email and verify_password(incoming_user.password, user.password) == True:
            return True
    return False


@app.post("/signup")
async def create_user(new_user: User = Body(...)) -> JSONResponse:
    """
    Creates a new user.

    :param new_user: The JSON body from the incoming request containing the user's signup credentials.
    :type new_user: User
    :return: Whether the new user was created successfully or not.
    :rtype: JSONResponse
    """
    for existing_user in database:
        if new_user.email == existing_user.email:
            return JSONResponse(content={"account_created": "false", "error": "user exists"}, status_code=409)
    new_user.password = get_password_hash(new_user.password)
    database.append(new_user)
    return JSONResponse(content={"account_created": True}, status_code=200)


@app.post("/login")
async def user_login(user: User = Body(...)) -> JSONResponse:
    """
    Authenticate the user.

    :param user: The JSON body from the incoming request containing the user's credentials.
    :type user: User
    :return: Whether the user logged in successfully or not.
    :rtype: JSONResponse
    """
    if check_user(user):
        return JSONResponse(content={"token": encode_token(user.email)}, status_code=200)
    return JSONResponse(content={"error": "wrong login details"}, status_code=401)


@app.get("/unprotected")
async def unprotected() -> JSONResponse:
    """
    Unprotected route. Authorization is not required.

    :return: The status of the request.
    :rtype: JSONResponse
    """
    return JSONResponse(content={"protected": False}, status_code=200)


@app.get("/protected")
async def protected(email=Depends(auth_wrapper)) -> JSONResponse:
    """
    Protected route. Authorization is required.

    :return: The status of the request.
    :rtype: JSONResponse
    """
    return JSONResponse(content={"protected": True}, status_code=200)


@app.post("/message")
async def add_message(email=Depends(auth_wrapper), message: Message = Body(...)) -> JSONResponse:
    """
    Adds user's message to the database. Authorization is required.

    :param email: The email from the decoded JWT.
    :type email: str
    :param message: The JSON body from the incoming request containing the user's message.
    :type message: Message
    :return: The status of the request.
    :rtype: JSONResponse
    """
    messages.append({"email": email, "message": message.content})
    return JSONResponse(content={"message": message.content, "status": "created"}, status_code=200)


@app.get("/message")
async def get_messages(email=Depends(auth_wrapper)) -> JSONResponse:
    """
    Retrieves all of the user's messages. Authorization is required.

    :param email: The email from the decoded JWT.
    :type email: str
    :return: The status of the request.
    :rtype: JSONResponse
    """
    user_messages = []
    for message in messages:
        if email == message["email"]:
            user_messages.append({"message": message["message"]})
    return JSONResponse(content=user_messages, status_code=200)
