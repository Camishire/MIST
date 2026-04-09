import requests
from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse
from typing import Optional, Dict
from app.config import settings


class OpenCTIAuth:
    OPENCTI_COOKIE_NAME = "opencti_session"
    
    @staticmethod
    async def verify_session(request: Request) -> Dict:
        # Get OpenCTI session cookie
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
        
        # Verify session with OpenCTI GraphQL API
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
            
            # Check if request successful
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
            
            # Check for GraphQL errors
            if "errors" in data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "Authentication failed",
                        "message": "Invalid OpenCTI session. Please login again.",
                        "opencti_url": settings.opencti_url
                    }
                )
            
            # Extract user info
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


# FastAPI dependency for route protection
async def require_opencti_auth(request: Request) -> Dict:
    return await OpenCTIAuth.verify_session(request)


# Optional: Check if user has specific capability
async def require_capability(capability_name: str):
    async def check_capability(request: Request) -> Dict:
        user = await OpenCTIAuth.verify_session(request)
        
        capabilities = [cap["name"] for cap in user.get("capabilities", [])]
        
        if capability_name not in capabilities:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Insufficient permissions",
                    "message": f"You need '{capability_name}' capability to access this resource.",
                    "required_capability": capability_name,
                    "user_capabilities": capabilities
                }
            )
        
        return user
    
    return check_capability