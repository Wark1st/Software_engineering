from fastapi import FastAPI
from Routes import router as routeRouter
from Trips import router as tripRouter


app = FastAPI()

app.include_router(routeRouter)
app.include_router(tripRouter)