from fastapi import FastAPI
from database import engine, get_db
import userModal as userModal

from Users import router as userRouter


userModal.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.include_router(userRouter)


