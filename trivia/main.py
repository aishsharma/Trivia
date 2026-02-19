from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from trivia.routers.categories import category_router
from trivia.routers.questions import question_router
from trivia.routers.quiz import quiz_router


# --------------------------------------------------
# APP INIT
# --------------------------------------------------

app = FastAPI(
    title="Trivia API",
    description="Backend API for Trivia Quiz App",
    version="1.0.0",
)


# --------------------------------------------------
# CORS (Frontend access)
# --------------------------------------------------

origins = [
    "http://localhost:3000",   # React / Vite
    "http://localhost:5173",   # Vite default
    "http://localhost:4321",   # Astro default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4321",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# ROUTERS
# --------------------------------------------------

app.include_router(category_router)
app.include_router(question_router)
app.include_router(quiz_router)


# --------------------------------------------------
# ROOT / HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Trivia API is running 🚀"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
