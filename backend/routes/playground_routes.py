from fastapi import APIRouter, Response
from sqlmodel import Session, select
from utils.cookie_utils import set_conditional_cookie
from db.test_model import TestTable, TestData
from database import engine
from utils.config_utils import get_settings

settings = get_settings()
router = APIRouter()

if settings.ENV == "dev":

    @router.get("/set-cookie")
    def set_cookie(response: Response):
        set_conditional_cookie(response=response, key="test_cookie", value="test_value")
        return {"message": "Cookie set"}

    @router.post("/insert")
    def insert_data(data: TestData):
        with Session(engine) as session:
            test_entry = TestTable(name=data.name)
            session.add(test_entry)
            session.commit()
            session.refresh(test_entry)
            return {"message": "Data inserted successfully", "id": test_entry.id}

    @router.delete("/delete")
    def delete_data():
        with Session(engine) as session:
            statement = select(TestTable)
            results = session.exec(statement)
            for test_entry in results:
                session.delete(test_entry)
            session.commit()
            return {"message": "All data deleted successfully"}