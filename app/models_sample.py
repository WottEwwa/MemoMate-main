from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class UsersWords(Base):
    __tablename__ = 'users_words'
    user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
    word_id = Column(Integer, ForeignKey('words.word_id'), primary_key=True)
    level_id = Column(Integer, ForeignKey('level.level_id'))
    correct_count = Column(Integer, default=0)
    
    user = relationship("User", back_populates="word_associations")
    word = relationship("Word", back_populates="user_associations")

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    user_name = Column(String)
    level_id = Column(Integer, ForeignKey('level.level_id'))
    from_code2 = Column(String)
    to_code2 = Column(String)
    
    word_associations = relationship("UsersWords", back_populates="user")

class Level(Base):
    __tablename__ = "level"
    level_id = Column(Integer, primary_key=True)
    de = Column(String)
    en = Column(String)
    es = Column(String)
    ua = Column(String)
    ru = Column(String)

class Word(Base):
    __tablename__ = "words"
    word_id = Column(Integer, primary_key=True)
    level_id = Column(Integer, ForeignKey('level.level_id'))
    de = Column(String)
    en = Column(String)
    es = Column(String)
    ua = Column(String)
    ru = Column(String)
    
    user_associations = relationship("UsersWords", back_populates="word")

def init_db():
    engine = create_engine('sqlite:///database_sample.db')
    Base.metadata.create_all(engine)
    return engine