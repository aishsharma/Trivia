from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from trivia.dependencies import get_db
from trivia.models import Question, Answer, Category
from trivia.schemas import QuestionCreate, QuestionRead


question_router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
)


# --- CREATE ---

@question_router.post("/", response_model=QuestionRead)
def create_question(
    data: QuestionCreate,
    db: Session = Depends(get_db),
):
    # Validate category
    if data.category_id:
        category = db.get(Category, data.category_id)
        if not category:
            raise HTTPException(400, "Invalid category_id")

    # Create question
    q = Question(
        text=data.text,
        category_id=data.category_id,
    )

    db.add(q)
    db.flush()  # Get ID without commit

    # Insert answers
    for ans in data.answers:
        a = Answer(
            text=ans.text,
            is_correct=ans.is_correct,
            question_id=q.id,
        )
        db.add(a)

    db.commit()
    db.refresh(q)

    return q


# --- LIST ---

@question_router.get("/", response_model=List[QuestionRead])
def list_questions(db: Session = Depends(get_db)):
    return (
        db.query(Question)
        .options(joinedload(Question.choices))
        .all()
    )


# --- GET ONE ---

@question_router.get("/{question_id}", response_model=QuestionRead)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
):
    q = (
        db.query(Question)
        .options(joinedload(Question.choices))
        .filter(Question.id == question_id)
        .first()
    )

    if not q:
        raise HTTPException(404, "Question not found")

    return q
