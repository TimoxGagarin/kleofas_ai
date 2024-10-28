from fastapi import status
from fastapi.exceptions import HTTPException

UnknownSSOProvider = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown SSO Provider")
Unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
SessionNotFound = HTTPException(status_code=403, detail="Session not found or expired")
AdminAccessRequired = HTTPException(status_code=403, detail="Admin access required")
