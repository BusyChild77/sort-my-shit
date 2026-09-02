from json import dumps as json_dumps, load as json_load
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from src.domain.entity.Theme import Theme
from src.infrastructure.repository.SettingsRepository import SettingsRepository


class SettingsRepositoryTest(TestCase):
    def setUp(self):
        self.run_dir = str(Path().resolve() / "tests/infrastructure/repository/SettingsRepositoryTest")
        Path(self.run_dir).mkdir(parents=True, exist_ok=True)

        self.settings_repository = SettingsRepository()
        self.settings_repository.runDir = self.run_dir

        super().setUp()

    def tearDown(self):
        rmtree(self.run_dir, ignore_errors=True)
        super().tearDown()

    def test_given_no_settings_file_when_fetching_settings_then_the_defaults_are_written(self):
        settings = self.settings_repository.fetch_all()

        self.assertEqual(settings, SettingsRepository.app_settings.default_user_settings)
        self.assertEqual(self.__written_settings(), SettingsRepository.app_settings.default_user_settings)

    def test_given_settings_missing_a_recent_option_when_fetching_settings_then_its_default_is_used(self):
        self.__given_settings({"destination_folder": "/destination"})

        self.assertFalse(self.settings_repository.fetch_one("preserve_folder_tree"))

    def test_given_settings_from_a_version_without_multiple_sources_when_fetching_settings_then_the_folder_is_migrated(self):
        self.__given_settings({"folder_to_process": "/downloads"})

        settings = self.settings_repository.fetch_all()

        self.assertEqual(settings["source_folders"], ["/downloads"])
        self.assertNotIn("folder_to_process", settings)

    def test_given_settings_from_a_version_with_flat_colors_when_fetching_settings_then_they_become_a_theme(self):
        self.__given_settings({
            "color1": "#000001",
            "color2": "#000002",
            "color3": "#000003",
            "color4": "#000004",
        })

        settings = self.settings_repository.fetch_all()

        self.assertEqual(settings["theme"]["background"], "#000001")
        self.assertEqual(settings["theme"]["surface"], "#000002")
        self.assertEqual(settings["theme"]["elevated"], "#000003")
        self.assertEqual(settings["theme"]["text"], "#000004")
        self.assertEqual(settings["theme"]["accent"], Theme.PRESETS[Theme.DEFAULT_PRESET]["accent"])
        self.assertNotIn("color1", settings)

    def test_given_a_saved_setting_when_fetching_it_back_then_the_saved_value_is_returned(self):
        self.__given_settings({})

        self.settings_repository.save_one("source_folders", ["/downloads", "/desktop"])

        self.assertEqual(self.settings_repository.fetch_one("source_folders"), ["/downloads", "/desktop"])

    def test_given_a_saved_setting_when_fetching_it_back_then_the_other_settings_are_kept(self):
        self.__given_settings({"destination_folder": "/destination"})

        self.settings_repository.save_one("preserve_folder_tree", True)

        self.assertEqual(self.settings_repository.fetch_one("destination_folder"), "/destination")

    def test_given_fetched_settings_when_the_returned_dict_is_changed_then_the_stored_settings_are_untouched(self):
        self.__given_settings({"destination_folder": "/destination"})

        self.settings_repository.fetch_all()["destination_folder"] = "/somewhere_else"

        self.assertEqual(self.settings_repository.fetch_one("destination_folder"), "/destination")

    def __given_settings(self, settings: dict):
        with open(self.run_dir + "/settings.json", "w") as settings_file:
            settings_file.write(json_dumps(settings))

    def __written_settings(self) -> dict:
        with open(self.run_dir + "/settings.json") as settings_file:
            return json_load(settings_file)
