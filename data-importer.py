from pathlib import Path

from trivia.db import SessionLocal
from trivia.models import Category, Question, Answer


# --- CONFIG ---

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Trivia-Data" / "categories"


# --- PARSER ---

def parse_question_block(lines, start_index):
    """
    Parses a variable-length question block.
    """

    if not lines[start_index].startswith("#Q"):
        raise ValueError(f"Invalid question start: {lines[start_index]}")

    question_parts = []
    i = start_index

    # Remove '#Q'
    question_parts.append(lines[i][2:].strip())
    i += 1

    # Collect question text
    while i < len(lines) and not lines[i].startswith("^"):
        question_parts.append(lines[i])
        i += 1

    if i >= len(lines):
        raise ValueError("Answer line not found")

    # Correct answer
    correct_answer = lines[i][1:].strip()
    i += 1

    # Choices
    choices = []

    while i < len(lines):

        line = lines[i]

        if line.startswith("#Q"):
            break

        if line.startswith("^"):
            break

        if len(line) < 2 or not line[0].isalpha():

            print("\n❌ BAD BLOCK AROUND LINE:")
            for x in range(i - 5, i + 10):
                if 0 <= x < len(lines):
                    print(f"{x}: {lines[x]}")

            raise ValueError(
                f"Invalid choice line: '{line}' at index {i}"
            )

        choices.append(line[1:].strip())
        i += 1

    question_text = "\n".join(question_parts).strip()

    if len(choices) < 2:
        raise ValueError(
            f"Too few choices for question: {question_text[:50]}"
        )

    return question_text, correct_answer, choices, i


# --- FILE READER ---

def read_file_lines(filepath):
    """
    Reads file with encoding fallback.
    """

    encodings_to_try = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin-1",
    ]

    for enc in encodings_to_try:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return [l.strip() for l in f if l.strip()]
        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"Unable to decode file: {filepath} (all encodings failed)"
    )


# --- IMPORTER ---

def import_file(filepath, session):

    category_name = filepath.stem

    print(f"\n📂 Importing category: {category_name}")

    # --- Get / create category ---

    category = (
        session.query(Category)
        .filter_by(name=category_name)
        .first()
    )

    if not category:
        category = Category(name=category_name)
        session.add(category)
        session.flush()
        print("  ➕ Created category")
    else:
        print("  ↺ Category exists")

    # --- Read file ---

    lines = read_file_lines(filepath)

    i = 0
    inserted_questions = 0

    while i < len(lines):

        if not lines[i].startswith("#Q"):
            i += 1
            continue

        (
            question_text,
            correct_answer,
            choices,
            next_index,
        ) = parse_question_block(lines, i)

        # --- Prevent duplicates ---

        existing = (
            session.query(Question)
            .filter_by(text=question_text)
            .first()
        )

        if existing:
            print(f"  ⚠ Skipping duplicate: {question_text[:50]}...")
            i = next_index
            continue

        # --- Insert question ---

        question = Question(
            category_id=category.id,
            text=question_text,
        )

        session.add(question)
        session.flush()

        # --- Insert answers ---

        if correct_answer not in choices:
            print(
                f"⚠ Answer not found in choices: "
                f"{correct_answer[:40]}..."
            )

        for choice_text in choices:
            answer = Answer(
                question_id=question.id,
                text=choice_text,
                is_correct=(choice_text == correct_answer),
            )
            session.add(answer)

        inserted_questions += 1
        i = next_index

    print(f"  ✅ Inserted {inserted_questions} questions")


# --- RUNNER ---

def run_import():

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data folder not found: {DATA_DIR}")

    session = SessionLocal()

    try:

        files = sorted(
            [f for f in DATA_DIR.iterdir() if f.is_file()]
        )

        if not files:
            print("No data files found.")
            return

        print(f"Found {len(files)} category files")

        for filepath in files:
            import_file(filepath, session)

        session.commit()
        print("\n🎉 Import complete!")

    except Exception as e:
        session.rollback()
        print("\n❌ Import failed. Rolled back.")
        raise e

    finally:
        session.close()


if __name__ == "__main__":
    run_import()
