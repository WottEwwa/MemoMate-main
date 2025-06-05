from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, func
from models.models import Base, User, Level, Word, UsersWords
from pydantic import BaseModel, ConfigDict
from typing import Optional
from sqlalchemy import text 

app = FastAPI()

# Async Engine Setup
engine = create_async_engine(
    'sqlite+aiosqlite:///database.db',
    connect_args={"check_same_thread": False},
    echo=True
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Dependency
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

# Pydantic models
class UserCreate(BaseModel):
    user_id: str
    user_name: str | None
    level_id: str
    from_code2: str
    to_code2: str

class UserResponse(BaseModel):
    user_id: str
    user_name: str
    level_id: str
    from_code2: str
    to_code2: str
    
    model_config = ConfigDict(from_attributes=True)

class WordCreate(BaseModel):
    level_id: str
    de: str
    en: Optional[str] = None
    es: Optional[str] = None
    ua: Optional[str] = None
    ru: Optional[str] = None

class WordUpdate(BaseModel):
    level_id: str
    en: Optional[str] = None
    es: Optional[str] = None
    ua: Optional[str] = None
    ru: Optional[str] = None

class WordResponse(BaseModel):
    word_id: int
    level_id: str
    de: str
    en: Optional[str] = None
    es: Optional[str] = None
    ua: Optional[str] = None
    ru: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class WordTranslationCheck(BaseModel):
    has_translation: bool

class WordRandomResponse(BaseModel):
    word_id: int
    de: str
    translation: str

# API endpoints 
@app.get("/")
async def root():
    return {"message": "MemoMate API running"}

@app.post("/users/create", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Level).where(Level.level_id == user.level_id))
    if not result.scalars().first():
        raise HTTPException(status_code=400, detail="Invalid level ID")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/words/create/", response_model=WordResponse, status_code=201)
async def create_word(word: WordCreate, db: AsyncSession = Depends(get_db)):
    # Überprüfe ob level existiert
    level_exists = await db.execute(select(Level).where(Level.level_id == word.level_id))
    if not level_exists.scalars().first():
        raise HTTPException(status_code=400, detail="Invalid level ID")
    
    word_data = {k: v for k, v in word.dict().items() if v is not None}
    db_word = Word(**word_data)
    db.add(db_word)
    await db.commit()
    await db.refresh(db_word)
    return db_word

@app.patch("/words/update/{word_de}", response_model=WordResponse)
async def update_word(
    word_de: str,
    word_update: WordUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Case-insensitive search for the word
    result = await db.execute(
        select(Word)
        .where(func.lower(Word.de) == func.lower(word_de))
    )
    db_word = result.scalars().first()
    
    if not db_word:
        raise HTTPException(
            status_code=404,
            detail=f"Word '{word_de}' not found"
        )
    
    # Prevent updating the German word itself
    if hasattr(word_update, 'de') and word_update.de is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot update German word text (de field). Use delete and create a new word instead."
        )
    
    # Apply updates
    update_data = word_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_word, field, value)
    
    await db.commit()
    await db.refresh(db_word)
    return db_word

@app.get("/words/translation/{to_code2}/{level}", response_model=WordTranslationCheck)
async def check_translation(
    to_code2: str,
    level: str,
    db: AsyncSession = Depends(get_db)
):
    # Validate target language
    valid_languages = ['en', 'es', 'ua', 'ru']
    if to_code2 not in valid_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target language. Must be one of: {valid_languages}"
        )

    # Find the word
    result = await db.execute(
        select(Word)
        .where(func.lower(Word.level_id) == func.lower(level))
    )
    db_word = result.scalars().first()

    if not db_word:
        raise HTTPException(
            status_code=404,
            detail=f"No translations for {to_code2}"
        )
    return {
        "has_translation": db_word[to_code2] is not None,
    }

@app.get("/words/random/{to_code2}", response_model=WordRandomResponse)
async def get_random_word(
    to_code2: str,
    db: AsyncSession = Depends(get_db),
    # Max tray
    max_attempts: int = 10
):
    valid_languages = ['en', 'es', 'ua', 'ru']
    if to_code2 not in valid_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid language code. Must be one of: {valid_languages}"
        )

    attempt = 0
    while attempt < max_attempts:
        result = await db.execute(
            select(Word)
            .where(getattr(Word, to_code2) != None)
            .order_by(func.random())
            .limit(1)
        )
        random_word = result.scalars().first()

        # Check 'translation' is not empty
        if random_word:
            translation = getattr(random_word, to_code2)
            if translation and str(translation).strip():
                return {
                    "word_id": random_word.word_id,
                    "de": random_word.de,
                    "translation": translation
                }

        attempt += 1

    # Falls keine gültige Übersetzung gefunden wurde
    raise HTTPException(
        status_code=404,
        detail=f"No words with valid {to_code2} translation found after {max_attempts} attempts"
    )


@app.post("/words/update_correct_count/{user_id}/{word_id}")
async def increment_correct_count(
    user_id: str,
    word_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Finde entry in users_words
    result = await db.execute(
        select(UsersWords)
        .where(UsersWords.user_id == user_id)
        .where(UsersWords.word_id == word_id)
    )
    user_word = result.scalars().first()
    
    if not user_word:
        user_word = UsersWords(
            user_id=user_id,
            word_id=word_id,
            correct_count=1
        )
        db.add(user_word)
    else:
        user_word.correct_count += 1
    
    await db.commit()
    await db.refresh(user_word)
    
    return {
        "user_id": user_id,
        "word_id": word_id,
        "new_count": user_word.correct_count
    }
    
@app.on_event("startup")
async def startup_event():
    await initialize_database()

async def initialize_database():
    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.execute(text("PRAGMA foreign_keys=ON"))
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully")

        # Add levels data
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Level))
            if not result.scalars().first():
                print("Adding levels data...")

                levels = [
                    Level(level_id="easy", de="leicht", en="easy", es="fácil", ua="легкий", ru="легкий"),
                    Level(level_id="hard", de="schwer", en="hard", es="difícil", ua="важкий", ru="тяжелый")
                ]
                
                db.add_all(levels)
                await db.commit()
                print("Levels data added successfully")

    except Exception as e:
        print(f"Critical initialization error: {str(e)}")
        raise
