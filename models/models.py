from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class UsersWords(Base):
    __tablename__ = 'users_words'
    user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
    level_id = Column(String, ForeignKey('level.level_id'))
    word_id = Column(Integer, ForeignKey('words.word_id'), primary_key=True)
    correct_count = Column(Integer, default=0)
    
    user = relationship("User", back_populates="word_associations")
    word = relationship("Word", back_populates="user_associations")
    level = relationship("Level", back_populates="user_words")

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    user_name = Column(String)
    level_id = Column(String, ForeignKey('level.level_id'))
    from_code2 = Column(String)
    to_code2 = Column(String)
    
    word_associations = relationship("UsersWords", back_populates="user")
    level = relationship("Level", back_populates="users")

class Level(Base):
    __tablename__ = "level"
    level_id = Column(String, primary_key=True)
    de = Column(String, unique=True)
    en = Column(String)
    es = Column(String)
    ua = Column(String)
    ru = Column(String)
    
    users = relationship("User", back_populates="level")
    words = relationship("Word", back_populates="level")
    user_words = relationship("UsersWords", back_populates="level")

class Word(Base):
    __tablename__ = "words"
    word_id = Column(Integer, primary_key=True, autoincrement=True)
    level_id = Column(String, ForeignKey('level.level_id'))
    de = Column(String, unique=True)
    en = Column(String)
    es = Column(String)
    ua = Column(String)
    ru = Column(String)
    
    user_associations = relationship("UsersWords", back_populates="word")
    level = relationship("Level", back_populates="words")

    def __getitem__(self, item):
        match item:
            case "de":
                return self.de
            case "en":
                return self.en
            case "es":
                return self.es
            case "ua":
                return self.ua
            case "ru":
                return self.ru
        return None
