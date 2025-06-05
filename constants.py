from enum import Enum


class LearningLevel(Enum):
    EASY = "beginner"
    HARD = "professional"

    @classmethod
    def from_str(cls, string: str | None):
        return LearningLevel[string]

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.name


class LearningLanguage(Enum):
    DE = "German"
    EN = "English"
    ES = "Spanish"
    UA = "Ukrainian"
    RU = "Russian"

    @classmethod
    def from_str(cls, string: str | None):
        return LearningLanguage[string]

    def code(self):
        return code_dict[self]

    def __str__(self):
        return self.value


code_dict = {
    LearningLanguage.DE: "DE",
    LearningLanguage.EN: "EN",
    LearningLanguage.ES: "ES",
    LearningLanguage.UA: "UA",
    LearningLanguage.RU: "RU",
}
