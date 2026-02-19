from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class CategoryUpdate(BaseModel):
    category: Optional[str] = None


class ChoiceBase(BaseModel):
    choice: str
    is_correct: bool = False


class ChoiceCreate(ChoiceBase):
    pass


class ChoiceUpdate(BaseModel):
    choice: Optional[str] = None
    is_correct: Optional[bool] = None


class ChoiceRead(ChoiceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class QuestionUpdate(BaseModel):
    categoryId: Optional[int] = None
    question: Optional[str] = None


# ---- ANSWERS ----

class AnswerBase(BaseModel):
    text: str
    is_correct: int = False


class AnswerCreate(AnswerBase):
    question_id: int


class AnswerRead(AnswerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)



# ---- QUESTIONS ----

class QuestionBase(BaseModel):
    text: str
    category_id: Optional[int] = None


class QuestionCreate(QuestionBase):
    answers: List[AnswerBase] = []


class QuestionRead(QuestionBase):
    id: int
    answers: List[AnswerRead] = []

    model_config = ConfigDict(from_attributes=True)



# ---- CATEGORIES ----

class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# QUIZ START
# ----------------------------

class QuizChoice(BaseModel):
    id: int
    text: str

    model_config = ConfigDict(from_attributes=True)


class QuizQuestion(BaseModel):
    id: int
    text: str
    choices: List[QuizChoice]

    model_config = ConfigDict(from_attributes=True)


class QuizStartResponse(BaseModel):
    category_name: Optional[str] = None
    questions: List[QuizQuestion]


# ----------------------------
# QUIZ SUBMIT
# ----------------------------

class QuizAnswerSubmit(BaseModel):
    answer_id: int


class QuizSubmitRequest(BaseModel):
    answers: List[QuizAnswerSubmit]


class QuizSubmitResponse(BaseModel):
    score: int
    total: int
    percentage: float
