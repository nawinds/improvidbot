from config import WHITE_SYMBOLS
from modules.logger import get_logger
from db import db_session
from db.aliases import Alias
import pymorphy2
import requests

logger = get_logger("text_func")
morph = pymorphy2.MorphAnalyzer()


def normalize(text):
    session = db_session.create_session()
    text = text.lower()
    text = text.replace("ё", "е")
    q = "".join(
        [i if i in WHITE_SYMBOLS else " " for i in text]).lower().split()
    alias_word = session.query(Alias).filter(Alias.word == text).first()
    for word in range(len(q)):
        alias = session.query(Alias).filter(Alias.alias == morph.parse(q[word])[0].normal_form).first()
        if alias and not alias_word:
            q[word] = alias.word.lower()
    return q


def get_text_variants(text):
    session = db_session.create_session()
    q = normalize(text)
    q2 = []
    short = []
    for word in q:
        alias = session.query(Alias).filter(Alias.alias == morph.parse(word)[0].normal_form).first()
        if alias:
            q2.append(alias)
            continue
        resp = requests.get(f"https://speller.yandex.net/services/"
                            f"spellservice.json/checkText?text={word}&options=512")
        if resp.json():
            if "error" not in resp.json()[0].keys():
                new = resp.json()[0]["s"][0]
                logger.warn(f"При поиске вариантов запроса была найдена опечатка: {word} -> {new}")
                alias = session.query(Alias).filter(Alias.alias == morph.parse(new)[0].normal_form).first()
                if alias:
                    q2.append(alias.word.lower())
                else:
                    q2.append(new)
                continue

        q2.append(word)
    #     for letter in word:
    #         if letter in RUSSIAN_LETTERS:
    #             ru_word = word
    #             en_word = "".join([LANG_ALIASES.get(letter, letter) for letter in word])
    #             break
    #         elif letter in ENGLISH_LETTERS:
    #             en_word = word
    #             ru_word = "".join([LANG_ALIASES.get(letter, letter) for letter in word])
    #             break
    #     ru_suggestions = list(ru_dict.suggest(ru_word))
    #     ru_max_measure, ru_best = 0, ru_word
    #
    #     for s in ru_suggestions:
    #         measure = difflib.SequenceMatcher(None, ru_word, s.lower()).ratio()
    #         if measure > ru_max_measure and measure > 0.7:
    #             ru_max_measure = measure
    #             ru_best = s.lower()
    #     en_suggestions = list(en_dict.suggest(en_word))
    #     en_max_measure, en_best = 0, en_word
    #     for s in en_suggestions:
    #         measure = difflib.SequenceMatcher(None, en_word, s.lower()).ratio()
    #         if measure > en_max_measure and measure > 0.7:
    #             en_max_measure = measure
    #             en_best = s.lower()
    #     if en_max_measure < 0.7 < ru_max_measure:
    #         q2.append(ru_best)
    #     elif en_max_measure > 0.7 > ru_max_measure:
    #         q2.append(en_best)
    #     elif ru_max_measure < 0.7 > en_max_measure:
    #         q2.append(word)
    #     elif ru_max_measure > en_max_measure:
    #         q2.append(ru_best)
    #     else:
    #         q2.append(en_best)
    variants = []
    for length in range(2, len(q2) + 1):
        for i in range(0, len(q2) - length + 1):
            variants.append(" ".join(q2[i:i + length]))
    for w in q2:
        short.append(w)
        nf = morph.parse(w)[0].normal_form
        if nf not in short:
            short.append(nf.lower())
    return variants, short
