from fastapi import Request
from typing import Dict

class OpenCTIAuth:
    @staticmethod
    async def verify_session(request: Request) -> Dict:
        return {
            "id": "test-user-123",
            "name": "Local Test User",
            "user_email": "test@localhost.dev"
        }
    
    @staticmethod
    def get_login_redirect():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="http://localhost:8000")


async def require_opencti_auth(request: Request) -> Dict:
    return await OpenCTIAuth.verify_session(request)