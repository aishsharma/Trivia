from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from trivia.dependencies import get_db
from trivia.models import Question, Answer, Category
from trivia.schemas import (
    QuizQuestion,
    QuizChoice,
    QuizStartResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
)


quiz_router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
)


# --------------------------------------------------
# START QUIZ
# --------------------------------------------------

@quiz_router.get("/start", response_model=QuizStartResponse)
def start_quiz(
    db: Session = Depends(get_db),
    category_id: Optional[int] = Query(
        None,
        description="Filter by category",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of questions",
    ),
    randomize: bool = Query(
        True,
        description="Randomize question order",
    ),
):
    """
    Fetch quiz questions.

    - Optional category filter
    - Limit question count
    - Randomized by default
    - Correct answers are NOT returned
    """

    query = db.query(Question).options(
        joinedload(Question.choices)
    )

    # --- Category filter ---
    if category_id is not None:
        exists = db.query(Category.id).filter_by(id=category_id).first()
        if not exists:
            raise HTTPException(404, "Category not found")
    
        query = query.filter(
            Question.category_id == category_id
        )

    # --- Random order ---
    if randomize:
        query = query.order_by(func.random())

    # --- Limit ---
    questions = query.limit(limit).all()

    if not questions:
        raise HTTPException(
            404,
            "No questions found for this quiz",
        )

    # --- Transform to quiz-safe schema ---
    quiz_questions: List[QuizQuestion] = []

    for q in questions:
        quiz_questions.append(
            QuizQuestion(
                id=q.id,
                text=q.text,
                choices=[
                    QuizChoice(
                        id=c.id,
                        text=c.text,
                    )
                    for c in q.choices
                ],
            )
        )

    category_name = None

    if category_id:
        category = (
            db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )

        if category:
            category_name = category.name.title()


    return QuizStartResponse(
        category_name=category_name,
        questions=quiz_questions
    )


# --------------------------------------------------
# SUBMIT QUIZ
# --------------------------------------------------

@quiz_router.post(
    "/submit",
    response_model=QuizSubmitResponse,
)
def submit_quiz(
    payload: QuizSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Submit quiz answers and calculate score.
    """

    if not payload.answers:
        raise HTTPException(
            400,
            "No answers submitted",
        )

    score = 0
    total = len(payload.answers)

    seen = set()

    for item in payload.answers:
        if item.answer_id in seen:
            raise HTTPException(
                400,
                f"Duplicate answer_id: {item.answer_id}"
            )
        seen.add(item.answer_id)

        answer = (
            db.query(Answer)
            .filter(Answer.id == item.answer_id)
            .first()
        )

        if not answer:
            raise HTTPException(
                400,
                f"Invalid answer_id: {item.answer_id}",
            )

        if answer.is_correct:
            score += 1

    percentage = (score / total) * 100 if total else 0

    return QuizSubmitResponse(
        score=score,
        total=total,
        percentage=round(percentage, 2),
    )
