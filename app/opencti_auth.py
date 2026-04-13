import requests
from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse
from typing import Optional, Dict
from app.config import settings

class OpenCTIAuth:
    OPENCTI_COOKIE_NAME = "opencti_session"
    
    @staticmethod
    async def verify_session(request: Request) -> Dict:
        opencti_session = request.cookies.get(OpenCTIAuth.OPENCTI_COOKIE_NAME)
        
        if not opencti_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "Not authenticated",
                    "message": "Please login to OpenCTI first",
                    "opencti_url": settings.opencti_url
                }
            )
        
        try:
            response = requests.post(
                f"{settings.opencti_url}/graphql",
                cookies={OpenCTIAuth.OPENCTI_COOKIE_NAME: opencti_session},
                json={
                    "query": """
                        query {
                            me {
                                id
                                name
                                user_email
                                capabilities {
                                    name
                                }
                            }
                        }
                    """
                },
                timeout=5
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "Invalid session",
                        "message": "Your OpenCTI session has expired. Please login again.",
                        "opencti_url": settings.opencti_url
                    }
                )
            
            data = response.json()
            
            if "errors" in data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "Authentication failed",
                        "message": "Invalid OpenCTI session. Please login again.",
                        "opencti_url": settings.opencti_url
                    }
                )
            
            user = data.get("data", {}).get("me")
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "No user data",
                        "message": "Could not retrieve user information from OpenCTI.",
                        "opencti_url": settings.opencti_url
                    }
                )
            
            return user
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "OpenCTI unavailable",
                    "message": f"Could not connect to OpenCTI: {str(e)}",
                    "opencti_url": settings.opencti_url
                }
            )
    
    @staticmethod
    def get_login_redirect() -> RedirectResponse:
        return RedirectResponse(
            url=f"{settings.opencti_url}/dashboard",
            status_code=status.HTTP_302_FOUND
        )


async def require_opencti_auth(request: Request) -> Dict:
    return await OpenCTIAuth.verify_session(request)
