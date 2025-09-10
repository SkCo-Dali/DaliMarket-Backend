# infrastructure/adapters/azure_auth_adapter.py
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException
from core.settings import settings
from application.ports.auth_port import AuthPort


class AzureAuthAdapter(AuthPort):
    def get_current_user(self, token: str) -> dict:
        try:
            jwks_client = PyJWKClient(f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/discovery/v2.0/keys")
            signing_key = jwks_client.get_signing_key_from_jwt(token).key

            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=settings.AZURE_CLIENT_ID,
            )

            return {
                "email": payload.get("preferred_username") or payload.get("upn"),
                "sub": payload.get("sub"),
            }

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado.")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
