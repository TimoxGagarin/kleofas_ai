from fastapi import HTTPException, status
from fastapi.exceptions import HTTPException


class EntityDoesntExist(HTTPException):
    def __init__(
        self,
        entity,
        status_code=status.HTTP_404_NOT_FOUND,
        detail="{} doesn't exist",
        headers=None,
    ):
        super().__init__(status_code, detail.format(entity), headers)


class EntityAlreadyExist(HTTPException):
    def __init__(
        self,
        entity,
        status_code=status.HTTP_409_CONFLICT,
        detail="{} already exist",
        headers=None,
    ):
        super().__init__(status_code, detail.format(entity), headers)


OnlyCSVAreSupported = HTTPException(
    status.HTTP_400_BAD_REQUEST, "Only CSV files are supported."
)
OnlyJSONAreSupported = HTTPException(
    status.HTTP_400_BAD_REQUEST, "Only JSON files are supported."
)
InvalidTableSchema = HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid table schema")
InvlaidJSONFormat = HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON format.")

UnknownSSOProvider = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Unknown SSO Provider"
)
Unauthorized = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
)
SessionNotFound = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Session not found or expired"
)
AdminAccessRequired = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
)

CourseAlreadyExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Course already exists"
)
CourseDoesntExists = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Course doesn't exist"
)
CourseIsntAvaliable = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Course isn't avaliable"
)

MessageDoesntExists = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Message doesn't exist"
)

UserDoesntExists = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist"
)
