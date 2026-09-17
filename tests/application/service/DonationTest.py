from os import path as os_path
from unittest import TestCase

from src.application.service.Donation import Donation


class DonationTest(TestCase):
    """The handle is written twice: once here, for the link on the Settings screen, and
    once in .github/FUNDING.yml, for the Sponsor button GitHub puts on the repository.
    Nothing breaks when the two drift -- the users who click one of them simply land on
    somebody else's page -- so they are held together here."""

    PROJECT = os_path.dirname(os_path.dirname(os_path.dirname(os_path.dirname(os_path.abspath(__file__)))))
    FUNDING_FILE = os_path.join(".github", "FUNDING.yml")
    PLATFORM = "buy_me_a_coffee"

    def test_given_the_funding_file_when_reading_its_handle_then_it_is_the_one_the_link_points_at(self):
        self.assertEqual(self.__funding()[self.PLATFORM], Donation.HANDLE)

    def test_given_the_link_when_reading_it_then_it_is_the_buymeacoffee_page_of_that_handle(self):
        self.assertEqual(Donation.URL, f"https://www.buymeacoffee.com/{Donation.HANDLE}")

    def test_given_the_link_when_reading_it_then_it_is_served_over_https(self):
        """A donation page reached over plain http is one a user should not be sent to."""
        self.assertTrue(Donation.URL.startswith("https://"))

    def test_given_the_monthly_link_when_reading_it_then_it_is_a_patreon_page_served_over_https(self):
        """The second door on the Support section, and a page asking a user for a card
        number, so it is held to the same rule as the first."""
        self.assertTrue(Donation.PATREON_URL.startswith("https://www.patreon.com/"))

    def test_given_the_monthly_link_when_reading_it_then_it_has_something_written_on_it(self):
        self.assertTrue(Donation.PATREON_CALL_TO_ACTION.strip())

    def test_given_the_copy_when_reading_it_then_the_section_has_something_to_show(self):
        self.assertTrue(Donation.BLURB.strip())
        self.assertTrue(Donation.CALL_TO_ACTION.strip())

    def __funding(self) -> dict:
        platforms = {}

        with open(os_path.join(self.PROJECT, self.FUNDING_FILE), encoding="utf-8") as funding_file:
            for line in funding_file:
                line = line.strip()

                if line.startswith("#") or ":" not in line:
                    continue

                platform, handle = line.split(":", 1)
                platforms[platform.strip()] = handle.strip().strip("[]")

        return platforms
