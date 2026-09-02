from os import path as os_path
from sys import argv as sys_argv
from tkinter import Tk

from src.application.service.EventManager import EventManager
from src.application.service.IconProvider import IconProvider
from src.application.service.SMSRenderer import SMSRenderer
from src.application.service.ThemeProvider import ThemeProvider
from src.application.view.AppearanceView import AppearanceView
from src.application.view.ConsoleView import ConsoleView
from src.application.view.RemoveDuplicatesView import RemoveDuplicatesView
from src.application.view.RemoveEmptyFilesView import RemoveEmptyFilesView
from src.application.view.RemoveEmptyFoldersView import RemoveEmptyFoldersView
from src.application.view.SettingsView import SettingsView
from src.application.view.SortFilesView import SortFilesView

from src.domain.service.compare.CompareBinary import CompareBinary
from src.domain.service.compare.CompareFileName import CompareFileName
from src.domain.service.list.ListDuplicate import ListDuplicate
from src.domain.service.remove.RemoveDuplicate import RemoveDuplicate
from src.domain.service.remove.RemoveEmptyFile import RemoveEmptyFile
from src.domain.service.remove.RemoveEmptyFolder import RemoveEmptyFolder
from src.domain.service.sort.PlanSort import PlanSort
from src.domain.service.sort.ResolveCategory import ResolveCategory
from src.domain.service.sort.SortFile import SortFile

from src.infrastructure.logger.LogFileLogger import LogFileLogger
from src.infrastructure.repository.FileInfoRepository import FileInfoRepository
from src.infrastructure.repository.FileSystemRepository import FileSystemRepository
from src.infrastructure.repository.SettingsRepository import SettingsRepository
from src.infrastructure.repository.TmpStorageRepository import TmpStorageRepository

from pysman.service_manager import ServiceManager
from src.manager.ViewManager import ViewManager


class SortMyShit:
    services = [
        EventManager,
        SettingsRepository,
        FileInfoRepository,
        FileSystemRepository,
        TmpStorageRepository,
        LogFileLogger,
        ThemeProvider,
        IconProvider,
        CompareFileName,
        CompareBinary,
        ResolveCategory,
        PlanSort,
        SortFile,
        ListDuplicate,
        RemoveEmptyFolder,
        RemoveEmptyFile,
        RemoveDuplicate,
        SMSRenderer,
    ]

    aliases = {
        "SettingsRepositoryInterface": SettingsRepository,
        "FileInfoRepositoryInterface": FileInfoRepository,
        "FileSystemRepositoryInterface": FileSystemRepository,
        "TmpStorageRepositoryInterface": TmpStorageRepository,
        "EventManagerInterface": EventManager,
    }

    views = {
        "sort_files": SortFilesView,
        "remove_duplicates": RemoveDuplicatesView,
        "remove_empty_files": RemoveEmptyFilesView,
        "remove_empty_folders": RemoveEmptyFoldersView,
        "console": ConsoleView,
        "settings": SettingsView,
        "appearance": AppearanceView,
    }

    def main():
        service_manager = ServiceManager()
        view_manager = ViewManager()
        view_manager.set_service_manager(service_manager)

        service_manager.register_aliases(SortMyShit.aliases)
        service_manager.autoload_services(SortMyShit.services)
        service_manager.get_service("SettingsRepository").runDir = os_path.dirname(os_path.abspath(sys_argv[0]))
        service_manager.get_service("LogFileLogger").activate_logging()

        root = Tk()

        view_manager.set_views(SortMyShit.views)

        service_manager.get_service("SMSRenderer").render(root, view_manager)

        root.mainloop()


if __name__ == "__main__":
    SortMyShit.main()
