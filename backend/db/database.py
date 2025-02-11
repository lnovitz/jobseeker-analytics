from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL, 
    echo=True, 
    connect_args={"check_same_thread": False}  
)

def create_db_and_tables():
    SQLModel.metadata.drop_all(engine)  
    SQLModel.metadata.create_all(engine)  

def get_session():
    return Session(engine)  # Opens a connection to interact with the database