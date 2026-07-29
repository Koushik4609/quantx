import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json

# For testing with the Firebase Auth Emulator
if os.environ.get("FIREBASE_AUTH_EMULATOR_HOST"):
    # Initialize without credentials when using the emulator
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
else:
    # Initialize with actual credentials in production
    # Requires a FIREBASE_SERVICE_ACCOUNT_JSON env var containing the JSON string
    service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if service_account_json and not firebase_admin._apps:
        cred_dict = json.loads(service_account_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    elif not firebase_admin._apps:
        # Fallback for testing when no emulator or service account is provided.
        # This will fail actual requests if hitting real Firebase services that require it,
        # but passing projectId allows verify_id_token to work by fetching public certs!
        firebase_admin.initialize_app(options={'projectId': 'quntax-9816c'})

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get the current user by verifying the Firebase ID token.
    Used in protected routes.
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        # decoded_token contains 'uid', 'email', etc.
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
