from fastapi import FastAPI
from database import engine, get_db
import Models.userModal as userModal

from Routes.Users import router as userRouter
from Routes.Points import router as pointRouter
from Routes.Routes import router as routeRouter
from Routes.Trips import router as tripRouter

import json

userModal.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(userRouter)
app.include_router(pointRouter)
app.include_router(routeRouter)
app.include_router(tripRouter)

