from vyklik.i18n import pl, ru

LANGUAGES = {"pl": pl.TR, "ru": ru.TR}
DEFAULT_LANGUAGE = "pl"
FALLBACK_CHAIN = {"pl": ["pl"], "ru": ["ru", "pl"]}


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: object) -> str:
    for code in FALLBACK_CHAIN.get(lang, [DEFAULT_LANGUAGE]):
        if key in LANGUAGES[code]:
            return LANGUAGES[code][key].format(**kwargs)
    return key
