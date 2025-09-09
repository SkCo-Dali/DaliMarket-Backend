# auth_azure.py
import os
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")  # App ID (tu backend / tu API)
JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        jwks_client = PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        # ✅ SOLO aceptamos tokens emitidos para TU API
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
        )

        # Extrae email del token
        email = (
            payload.get("preferred_username")
            or payload.get("upn")
            or (payload.get("email") if isinstance(payload.get("email"), str) else None)
            or (payload.get("emails")[0] if isinstance(payload.get("emails"), list) and payload.get("emails") else None)
        )
        if not email:
            raise HTTPException(status_code=401, detail="No se encontró el correo en el token.")

        return {
            "email": email,
            "sub": payload.get("sub"),
            "tid": payload.get("tid"),
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
