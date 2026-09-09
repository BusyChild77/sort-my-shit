from unittest import TestCase
from unittest.mock import Mock

from src.domain.entity.FolderState import FolderState
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface
from src.domain.service.folder.CheckFolder import CheckFolder


class CheckFolderTest(TestCase):
    def setUp(self):
        self.event_manager_mock = Mock(EventManagerInterface)
        self.file_system_repository_mock = Mock(FileSystemRepositoryInterface)

        self.folder_check = CheckFolder(
            self.event_manager_mock,
            self.file_system_repository_mock,
        )

        super().setUp()

    def test_given_folders_that_answered_when_checking_them_then_they_are_all_readable(self):
        self.file_system_repository_mock.probe_folder.return_value = FolderState.READABLE

        self.assertEqual(
            self.folder_check.readable(["/downloads", "/desktop"]),
            (["/downloads", "/desktop"], []),
        )

    def test_given_a_share_that_did_not_answer_when_checking_folders_then_it_is_not_walked(self):
        """The one answer that must never be given is "nothing found": a folder that
        could not be read is dropped from the scan rather than walked and found empty."""
        self.file_system_repository_mock.probe_folder.side_effect = [
            FolderState.READABLE,
            FolderState.UNREACHABLE,
        ]

        self.assertEqual(
            self.folder_check.readable(["/downloads", "/mnt/nas"]),
            (["/downloads"], ["/mnt/nas"]),
        )

    def test_given_a_folder_that_is_not_there_when_checking_folders_then_it_is_not_walked(self):
        self.file_system_repository_mock.probe_folder.return_value = FolderState.MISSING

        self.assertEqual(self.folder_check.readable(["/gone"]), ([], ["/gone"]))

    def test_given_a_share_that_did_not_answer_when_checking_folders_then_it_is_reported(self):
        self.file_system_repository_mock.probe_folder.return_value = FolderState.UNREACHABLE

        self.folder_check.readable(["/mnt/nas"])

        self.event_manager_mock.trigger.assert_called_once()
        self.assertIn("/mnt/nas", self.event_manager_mock.trigger.call_args.args[1])
        self.assertIn("did not answer", self.event_manager_mock.trigger.call_args.args[1])

    def test_given_folders_when_checking_them_then_the_probe_carries_the_deadline(self):
        self.file_system_repository_mock.probe_folder.return_value = FolderState.READABLE

        self.folder_check.readable(["/downloads"])

        self.file_system_repository_mock.probe_folder.assert_called_once_with(
            "/downloads", CheckFolder.TIMEOUT_IN_SECONDS
        )

    def test_given_a_destination_that_is_not_there_yet_when_checking_it_then_it_is_reachable(self):
        """It gets created on the way, which is not the same as a destination behind a
        mount that says nothing."""
        self.file_system_repository_mock.probe_folder.return_value = FolderState.MISSING

        self.assertTrue(self.folder_check.reachable("/destination"))

    def test_given_a_destination_that_did_not_answer_when_checking_it_then_it_is_not_reachable(self):
        self.file_system_repository_mock.probe_folder.return_value = FolderState.UNREACHABLE

        self.assertFalse(self.folder_check.reachable("/mnt/nas/sorted"))

    def test_given_folders_that_could_not_be_read_when_warning_then_the_count_is_said(self):
        self.assertEqual(
            self.folder_check.warning(["/mnt/nas", "/gone"]),
            " 2 folder(s) could not be read and were skipped.",
        )

    def test_given_no_folder_that_could_not_be_read_when_warning_then_nothing_is_said(self):
        self.assertEqual(self.folder_check.warning([]), "")
