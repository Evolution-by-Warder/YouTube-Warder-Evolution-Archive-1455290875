"""Live Enigma2 language selection drives Warder UI without user overrides."""
import importlib.util
import json
import re
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

P = Path(__file__).resolve().parents[1] / "plugin/Plugins/Extensions/WarderYouTube/i18n.py"
spec = importlib.util.spec_from_file_location("_warder_locales", P)
lang = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lang)


class LanguageTests(unittest.TestCase):
    def translate(self, code, phrase):
        components = types.ModuleType("Components")
        components.__path__ = []
        language = types.ModuleType("Components.Language")
        language.language = types.SimpleNamespace(getLanguage=lambda: code)
        with patch.dict(sys.modules, {"Components": components, "Components.Language": language}):
            return lang.tr(phrase)

    def test_language_is_read_from_enigma2(self):
        self.assertEqual(self.translate("sk_SK", "Search"), "Hľadať")
        self.assertEqual(self.translate("cs_CZ", "Search"), "Hledat")
        self.assertEqual(self.translate("de_DE", "Search"), "Suche")
        self.assertEqual(self.translate("en_GB", "Search"), "Search")

    def test_single_favourite_removal_is_distinct_from_clear_all(self):
        strings = {
            "sk_SK": ("Odobrať z obľúbených", "Vymazať všetky obľúbené",
                      "Vymazať celú históriu", "Vymazať všetko"),
            "cs_CZ": ("Odebrat z oblíbených", "Vymazat všechny oblíbené",
                      "Vymazat celou historii", "Vymazat vše"),
            "de_DE": ("Aus Favoriten entfernen", "Alle Favoriten löschen",
                      "Gesamten Verlauf löschen", "Alles löschen"),
            "en_GB": ("Remove from favourites", "Clear all favourites",
                      "Clear entire history", "Clear all")
        }
        for locale, expected in strings.items():
            with self.subTest(locale=locale):
                values = tuple(self.translate(locale, key) for key in (
                    "Remove from favourites", "Clear all favourites",
                    "Clear entire history", "Clear all"
                ))
                self.assertEqual(values, expected)

    def test_all_destructive_actions_specify_their_target_in_every_language(self):
        keys = (
            "Remove video from favourites", "Clear all favourite videos",
            "Delete video from history", "Clear entire history",
            "Clear favourites", "Clear history", "Delete from history",
            "Delete character", "Add video to favourites",
        )
        values = {
            "sk_SK": (
                "Odobrať video z obľúbených", "Vymazať všetky obľúbené videá",
                "Zmazať video z histórie", "Vymazať celú históriu",
                "Vymazať obľúbené", "Vymazať históriu",
                "Zmazať z histórie", "Zmazať znak", "Pridať video do obľúbených",
            ),
            "cs_CZ": (
                "Odebrat video z oblíbených", "Vymazat všechna oblíbená videa",
                "Smazat video z historie", "Vymazat celou historii",
                "Vymazat oblíbené", "Vymazat historii",
                "Smazat z historie", "Smazat znak", "Přidat video do oblíbených",
            ),
            "de_DE": (
                "Video aus Favoriten entfernen", "Alle Favoritenvideos löschen",
                "Video aus Verlauf löschen", "Gesamten Verlauf löschen",
                "Favoriten löschen", "Verlauf löschen",
                "Aus Verlauf löschen", "Zeichen löschen",
                "Video zu Favoriten hinzufügen",
            ),
            "en_GB": keys,
        }
        for language, expected in values.items():
            with self.subTest(language=language):
                translated = tuple(self.translate(language, label) for label in keys)
                self.assertEqual(translated, expected)

    def test_library_key_legends_name_history_or_favourites(self):
        keys = (
            "OK: play · INFO: details · MENU: actions · YELLOW: remove favourite · BLUE: clear favourites · EXIT: home",
            "OK: play · INFO: details · MENU: actions · YELLOW: delete from history · BLUE: clear history · EXIT: home",
        )
        for language in ("sk_SK", "cs_CZ", "de_DE", "en_GB"):
            with self.subTest(language=language):
                favourite, history = tuple(self.translate(language, key) for key in keys)
                self.assertNotEqual(favourite, history)
                self.assertTrue(favourite)
                self.assertTrue(history)
                self.assertNotIn("YELLOW: delete from history", favourite)
                self.assertNotIn("BLUE: clear favourites", history)

    def test_key_legends_follow_receiver_language(self):
        self.assertEqual(self.translate("sk_SK", "Updates"), "Aktualizácie")
        self.assertEqual(self.translate("cs_CZ", "Updates"), "Aktualizace")
        self.assertEqual(self.translate("de_DE", "Updates"), "Updates")
        self.assertEqual(self.translate("en_GB", "Updates"), "Updates")

    def test_settings_slovak_string_falls_back_to_english(self):
        source = "API kľúč: nastavený"
        self.assertEqual(self.translate("sk_SK", source), source)
        self.assertEqual(self.translate("en_GB", source), "API key: configured")
        self.assertEqual(self.translate("xx_XX", source), "API key: configured")

    def test_default_german_and_czech_status(self):
        source = "Testovací kanál: používate najnovšiu dostupnú verziu."
        self.assertIn("Testkanal", self.translate("de_DE", source))
        self.assertIn("Testovací", self.translate("cs_CZ", source))

    def test_external_catalogues_have_exact_keys_and_format_arguments(self):
        keys = set().union(*(catalog.keys() for catalog in lang.MESSAGES.values()))
        placeholders = re.compile(r"%(?:\([^)]+\))?[-+#0 ]*\d*(?:\.\d+)?[diouxXeEfFgGcrsa%]")
        paths = list((P.parent / "locale").glob("*.json"))
        self.assertEqual({path.stem for path in paths}, set(lang.LANGUAGES) - set(lang.MESSAGES))
        self.assertEqual(len(lang.LANGUAGES), 21)
        for path in paths:
            with self.subTest(language=path.stem):
                self.assertIn(path.stem, lang.LANGUAGES)
                values = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(set(values), keys)
                for key, value in values.items():
                    self.assertIsInstance(value, str)
                    self.assertTrue(value.strip(), key)
                    source = lang.MESSAGES["en"].get(key, key)
                    self.assertEqual(placeholders.findall(value), placeholders.findall(source), key)
                    self.assertEqual(self.translate(path.stem, key), value)

    def test_russian_runtime_and_aliases(self):
        self.assertEqual(self.translate("ru_RU", "Search"), lang.external_catalog("ru")["Search"])
        self.assertNotEqual(self.translate("ru_RU", "Search"), "Search")
        for alias, canonical in lang.ALIASES.items():
            self.assertEqual(self.translate(alias, "Search"), self.translate(canonical, "Search"))
        self.assertEqual(self.translate("../../etc", "Search"), "Search")

    def test_extra_runtime_messages_cover_all_languages(self):
        extra = lang.extra_catalogs()
        self.assertEqual(set(extra), set(lang.LANGUAGES))
        keys = set(extra["en"])
        self.assertGreaterEqual(len(keys), 57)
        for code, values in extra.items():
            self.assertEqual(set(values), keys)
            for key, value in values.items():
                self.assertIsInstance(value, str)
                self.assertTrue(value.strip())
                self.assertEqual(self.translate(code, key), value)
        self.assertEqual(self.translate("xx_XX", "Prihlásenie do YouTube"), "Sign in to YouTube")

    def test_update_error_messages_keep_diagnostic_code_in_all_languages(self):
        import ast
        source = (P.parent / "update_core.py").read_text(encoding="utf-8")
        keys = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "UpdateError" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.BinOp):
                    arg = arg.left
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    keys.add(arg.value)
        for code in lang.LANGUAGES:
            self.assertTrue(keys <= set(lang.extra_catalogs()[code]), code)
            with patch.object(lang, "language_code", return_value=code):
                self.assertIn("-7", lang.update_error_text("Inštalácia opkg skončila chybou (-7)."))
                self.assertEqual(lang.update_error_text("Balík je nekompletný."), lang.extra_catalogs()[code]["Balík je nekompletný."])

    def test_unknown_keys_stay_human_readable(self):
        self.assertEqual(self.translate("en_GB", "Warder Evolution"), "Warder Evolution")


if __name__ == "__main__":
    unittest.main()
