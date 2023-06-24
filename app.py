from fastapi import FastAPI, Depends, Request, Form, status, Response

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "todo_list": todos}
    )


@app.post("/add")
def add(request: Request, title: str = Form(...), db: Session = Depends(get_db)):
    new_todo = models.Todo(title=title)
    db.add(new_todo)
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/update/{todo_id}")
def update(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).get(todo_id)
    if todo is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="Todo not found")
    todo.complete = not todo.complete
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/delete/{todo_id}")
def delete(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).get(todo_id)
    if todo is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="Todo not found")
    db.delete(todo)
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.post("/edit/{todo_id}")
def edit_todo(todo_id: int, title: str = Form(...), db: Session = Depends(get_db)):
    todo = db.query(models.Todo).get(todo_id)
    if todo is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="Todo not found")
    todo.title = title
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
