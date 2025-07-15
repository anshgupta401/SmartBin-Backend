from fastapi import FastAPI
from routers import auth, bins
from database import base,engine

app = FastAPI()
app.include_router(auth.router,prefix="/api")
app.include_router(bins.router,prefix="/data")
base.metadata.create_all(bind=engine)

app.get("/")
def route():
    return {"message":"okay"}
