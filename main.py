from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import json

app = FastAPI()

db_file = "movies.json"

# Определение модели для запроса и ответа
class MovieResponse(BaseModel):
    name: str = Field(..., min_length=1, description="Название фильма")
    plot: str = Field(..., min_length=1, description="Сюжет")
    genres: List[str] = Field(..., min_length=1, description="Жанры фильма")
    casts: List[str] = Field(..., min_length=1, description="Актерский состав")

# Определение модели для хранения данных о фильмах в базе данных
class MovieDB(MovieResponse):
    id: int = Field(..., description="id фильма в базе")


# Загрузка базы
try:
    with open(db_file, 'r', encoding='utf-8') as db:
        movie_db = [MovieDB(**item) for item in json.load(db)]
except FileNotFoundError:
    movie_db = []

# Сохранение базы
def save_db():
    with open(db_file, 'w', encoding='utf-8') as db:
        json.dump([m.model_dump() for m in movie_db], db, indent=4, ensure_ascii=False)

# Получить следующий id для нового фильма
def get_next_id() -> int:
    if not movie_db:
        return 1
    return max(m.id for m in movie_db) + 1

# Найти индекс фильма по id
def find_movie_index(movie_id: int) -> int:
    for index, movie in enumerate(movie_db):
        if movie.id == movie_id:
            return index
    return -1

# Получить список всех фильмов
@app.get("/", response_model=List[MovieDB])
async def get_all_movies():
    return movie_db

#Получить фильм по id
@app.get("/{movie_id}", response_model=MovieDB)
async def get_movie(movie_id: int):
    
    index = find_movie_index(movie_id)
    if index == -1:
        raise HTTPException(status_code=404, detail="Movie with given id not found")
    return movie_db[index]


#Добавить фильм
@app.post("/", status_code=201, response_model=MovieDB)
async def add_movie(payload: MovieResponse):
    new_movie = MovieDB(id=get_next_id(), **payload.model_dump())
    movie_db.append(new_movie)
    save_db()
    return new_movie


#Удалить фильм по id
@app.delete("/{movie_id}", status_code=204)
async def delete_movie(movie_id: int):
    
    index = find_movie_index(movie_id)
    if index == -1:
        raise HTTPException(status_code=404, detail="Movie with given id not found")

    del movie_db[index]
    save_db()
    return None