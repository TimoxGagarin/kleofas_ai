from fastapi import status
from fastapi.exceptions import HTTPException

UnknownSSOProvider = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown SSO Provider")
Unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
SessionNotFound = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session not found or expired")
AdminAccessRequired = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

CourseAlreadyExists = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course already exists")
CourseDoesntExists = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course doesn't exist")
CourseIsntAvaliable = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Course isn't avaliable")

MessageDoesntExists = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message doesn't exist")

UserDoesntExists = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist")
