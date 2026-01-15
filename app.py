from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from models import ReviewInput, ReviewOutput
import crud

app = FastAPI()

@app.post("/api/review")
def create_review(review: ReviewInput):
    crud.create_review(review)
    return {"message": "Review added"}

@app.get("/api/review/{movie_title}")
def read_reviews(movie_title: str):
    return crud.get_reviews_with_similar(movie_title)

@app.patch("/api/review/{review_id}")
def update_review(review_id: str, data: dict):
    crud.update_review(review_id, data["summary"], data["rating"])
    return {"message": "Review updated"}

@app.delete("/api/review/{review_id}")
def delete_review(review_id: str):
    crud.delete_review(review_id)
    return {"message": "Review deleted"}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
