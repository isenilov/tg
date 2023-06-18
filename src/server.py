from fastapi import FastAPI
from pydantic import BaseModel
from .model import CategorizationModel

app = FastAPI()

model = CategorizationModel("model")


class Overview(BaseModel):
    overview: str


@app.post("/")
def predict(overview: Overview):
    return {"genres": model.predict(overview.overview)}
