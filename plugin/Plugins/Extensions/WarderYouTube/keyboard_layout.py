# -*- coding: utf-8 -*-
"""Single locale-aware Warder keyboard matrix shared by full and inline editors.

Only the view changes between them. Character rows and remote navigation
semantics remain identical; no third-party renderer or system keyboard patch.
"""
from .i18n import language_code

COLUMNS = 10
KEYBOARDS = {
    "sk": ("1234567890", "qwertyuiop", "asdfghjkl-", "zxcvbnm.,?", "áčďéíľňšťž"),
    "cs": ("1234567890", "qwertyuiop", "asdfghjkl-", "zxcvbnm.,?", "áčďéěíňřšť"),
    "de": ("1234567890", "qwertzuiop", "asdfghjkl-", "yxcvbnm.,?", "äöüßéèàâêî"),
    "en": ("1234567890", "qwertyuiop", "asdfghjkl-", "zxcvbnm.,?", "@#:/_()+*?"),
}
# Fixed 50-key fallback; Enigma2's native keyboard remains available for
# full language input, including Chinese IME where supported by the image.
def _latin(accents):
    return KEYBOARDS["en"][:4] + (accents,)


def _alphabet(letters):
    chars = (letters + "-.,?@#:/_()+*!=")[:40]
    return ("1234567890",) + tuple(chars[i:i+10] for i in range(0, 40, 10))


KEYBOARDS.update({
    "pl": _latin("ąćęłńóśźż!"),
    "hu": _latin("áéíóöőúüű!"),
    "fr": _latin("àâçéèêëîôù"),
    "it": _latin("àèéìòù@#:/"),
    "es": _latin("áéíóúüñ¿¡!"),
    "al": _latin("ëç@#:/_()+"),
    "et": _latin("õäöüšž@#:/"),
    "lt": _latin("ąčęėįšųūž!"),
    "nl": _latin("éèëïöüáàê!"),
    "pt": _latin("áàâãçéêíóõ"),
    "ro": _latin("ăâîșț@#:/_"),
    "tr": _latin("çğıöşüİ@#?"),
    "ru": _alphabet("абвгдеёжзийклмнопрстуфхцчшщъыьэюя"),
    "uk": _alphabet("абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"),
    "el": _alphabet("αβγδεζηθικλμνξοπρστυφχψωςάέήίόύώϊϋ"),
    "fa": _alphabet("ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"),
    "zh": KEYBOARDS["en"],  # ASCII/pinyin fallback, not a Chinese IME.
})
ROWS = KEYBOARDS["sk"]


def keyboard_rows(locale=None):
    """Select the same 5x10 character layout in both Warder keyboards."""
    selected = (locale or language_code()).split("_")[0].split("-")[0].lower()
    selected = {"sq": "al", "gr": "el", "cz": "cs", "ua": "uk", "cn": "zh"}.get(selected, selected)
    return KEYBOARDS.get(selected, KEYBOARDS["en"])
