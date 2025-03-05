import datetime
import logging
import os

from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from googleapiclient.discovery import build

from constants import QUERY_APPLIED_EMAIL_FILTER
from utils.auth_utils import AuthenticatedUser
from utils.db_utils import export_to_csv
from utils.email_utils import (
    get_email_ids,
    get_email,
)
from utils.file_utils import get_user_filepath
from utils.llm_utils import process_email
from utils.config_utils import get_settings
from session.session_layer import validate_session

# Import Google login routes
from login.google_login import router as google_login_router

from pydantic import BaseModel
from sqlmodel import SQLModel, create_engine, Session, Field, select

app = FastAPI()
settings = get_settings()
APP_URL = settings.APP_URL
app.add_middleware(SessionMiddleware, secret_key=settings.COOKIE_SECRET)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[APP_URL],  # Allow frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(message)s")

api_call_finished = False

# Database setup
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)


class TestTable(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    __tablename__ = "test_table"


SQLModel.metadata.create_all(engine)


class TestData(BaseModel):
    name: str


if settings.ENV == "dev":

    @app.post("/insert")
    def insert_data(data: TestData):
        with Session(engine) as session:
            test_entry = TestTable(name=data.name)
            session.add(test_entry)
            session.commit()
            session.refresh(test_entry)
            return {"message": "Data inserted successfully", "id": test_entry.id}

    @app.delete("/delete")
    def delete_data():
        with Session(engine) as session:
            statement = select(TestTable)
            results = session.exec(statement)
            for test_entry in results:
                session.delete(test_entry)
            session.commit()
            return {"message": "All data deleted successfully"}


@app.get("/")
async def root(request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse("homepage.html", {"request": request})


@app.get("/processing", response_class=HTMLResponse)
async def processing(request: Request, user_id: str = Depends(validate_session)):
    logging.info("user_id:%s processing", user_id)
    global api_call_finished
    if not user_id:
        logger.info("user_id: not found, redirecting to login")
        return RedirectResponse("/logout", status_code=303)
    if api_call_finished:
        logger.info("user_id: %s processing complete", user_id)
        return JSONResponse(
            content={
                "message": "Processing complete",
                "redirect_url": f"{APP_URL}/success",
            }
        )
    else:
        logger.info("user_id: %s processing not complete for file", user_id)
        return JSONResponse(content={"message": "Processing in progress"})


@app.get("/download-file")
async def download_file(request: Request, user_id: str = Depends(validate_session)):
    if not user_id:
        return RedirectResponse("/logout", status_code=303)
    directory = get_user_filepath(user_id)
    filename = "emails.csv"
    filepath = f"{directory}/{filename}"
    if os.path.exists(filepath):
        logger.info("user_id:%s downloading from filepath %s", user_id, filepath)
        return FileResponse(filepath)
    return HTMLResponse(content="File not found :( ", status_code=404)


@app.get("/logout")
async def logout(request: Request, response: RedirectResponse):
    logger.info("Logging out")
    request.session.clear()
    response.delete_cookie(key="Authorization")
    return RedirectResponse("/", status_code=303)


def fetch_emails(user: AuthenticatedUser) -> None:
    global api_call_finished

    api_call_finished = False  # this is helpful if the user applies for a new job and wants to rerun the analysis during the same session
    logger.info("user_id:%s fetch_emails", user.user_id)
    service = build("gmail", "v1", credentials=user.creds)
    messages = get_email_ids(query=QUERY_APPLIED_EMAIL_FILTER, gmail_instance=service)

    # Directory to save the emails
    os.makedirs(user.filepath, exist_ok=True)
    # if we're developing, flush the emails output instead of appending to it.
    if settings.ENV == "dev" and os.path.isfile(
        os.path.join(user.filepath, "emails.csv")
    ):
        os.remove(os.path.join(user.filepath, "emails.csv"))

    if len(messages) > 1000:
        logger.warning(
            f"**************detected {len(messages)} that passed the filter!"
        )

    for idx, message in enumerate(messages):
        message_data = {}
        # (email_subject, email_from, email_domain, company_name, email_dt)
        msg_id = message["id"]
        logger.info(
            f"user_id:{user.user_id} begin processing for email {idx + 1} of {len(messages)} with id {msg_id}"
        )
        msg = get_email(message_id=msg_id, gmail_instance=service)
        if msg:
            result = process_email(msg["text_content"])
            if not isinstance(result, str) and result:
                logger.info(
                    f"user_id:{user.user_id} successfully extracted email {idx + 1} of {len(messages)} with id {msg_id}"
                )
            else:
                result = {}
                logger.warning(
                    f"user_id:{user.user_id} failed to extract email {idx + 1} of {len(messages)} with id {msg_id}"
                )
            message_data["company_name"] = [result.get("company_name", "")]
            message_data["application_status"] = [result.get("application_status", "")]
            message_data["received_at"] = [msg.get("date", "")]
            message_data["subject"] = [msg.get("subject", "")]
            message_data["from"] = [msg.get("from", "")]

            # expose the message id on the dev environment
            if settings.ENV == "dev":
                message_data["id"] = [msg_id]
            # Exporting the email data to a CSV file
            export_to_csv(user.filepath, user.user_id, message_data)
    api_call_finished = True


@app.get("/success", response_class=HTMLResponse)
def success(request: Request, user_id: str = Depends(validate_session)):
    if not user_id:
        return RedirectResponse("/logout", status_code=303)
    today = str(datetime.date.today())
    return templates.TemplateResponse(
        "success.html", {"request": request, "today": today}
    )


# Register Google login routes
app.include_router(google_login_router)

# Run the app using Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
