import datetime
import logging
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from google_auth_oauthlib.flow import Flow

from utils.auth_utils import AuthenticatedUser
from session.session_layer import create_random_session_string
from utils.config_utils import get_settings
# from main import fetch_emails

# Logger setup
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# FastAPI router for Google login
router = APIRouter()


@router.get("/login")
async def login(request: Request, background_tasks: BackgroundTasks):
    code = request.query_params.get("code")
    flow = Flow.from_client_secrets_file(
        settings.CLIENT_SECRETS_FILE,
        settings.GOOGLE_SCOPES,
        redirect_uri=settings.REDIRECT_URI,
    )

    try:
        if not code:
            authorization_url, state = flow.authorization_url(prompt="consent")
            return RedirectResponse(url=authorization_url)

        flow.fetch_token(code=code)
        creds = flow.credentials

        if not creds.valid:
            creds.refresh(Request())
            return RedirectResponse("/login", status_code=303)

        user = AuthenticatedUser(creds)
        session_id = request.session["session_id"] = create_random_session_string()

        # Set session details
        try:
            token_expiry = creds.expiry.isoformat()
        except Exception as e:
            logger.error("Failed to parse token expiry: %s", e)
            token_expiry = (
                datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            ).isoformat()

        request.session["token_expiry"] = token_expiry
        request.session["user_id"] = user.user_id
        request.session["creds"] = creds.to_json() 

        response = RedirectResponse(url=f"{settings.APP_URL}/dashboard?user_id={user.user_id}", status_code=303)
        response.set_cookie(
            key="Authorization", value=session_id, secure=True, httponly=True
        )

        logger.info("User logged in with user_id: %s", user.user_id)
        logger.info(f"Session after login: {request.session}")  # Debugging

        return response
    except Exception as e:
        logger.error("Login error: %s", e)
        return HTMLResponse(content="An error occurred, sorry!", status_code=500)
