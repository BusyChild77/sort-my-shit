from src.domain.entity.Theme import Theme


class Settings:
    """The defaults, and what an older settings file is migrated from, see
    .claude/recipes/settings.md:17. renamed_user_settings maps a legacy name to its
    current one, folder_list_user_settings lists the settings once holding a single
    folder, and legacy_theme_colors maps a flat color used before the "theme" setting to
    the theme color it became."""

    default_type_mapping = {
        "docs": [
            "pdf", "pdf_lbk", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
            "txt", "odt", "ods", "odp", "md", "rtf", "csv", "html"
        ],
        "pics": [
            "jpg", "jpg_lbk", "jpeg", "jpeg_lbk", "png", "gif", "webp"
        ],
        "compressed": [
            "zip", "rar", "tar", "gz", "7z", "xz", "bz2", "tgz", "tbz", "tbz2", "txz",
            "tzst", "zst", "lz", "lzma", "lz4", "z", "cab", "arj", "lzh", "zipx", "cpio"
        ],
        "audio": [
            "mp3", "wma", "wav", "flac", "ogg", "m4a", "m4a_lbk", "aac"
        ],
        "video": [
            "m4v", "webm", "mp4", "avi", "mkv", "flv", "mov", "wmv"
        ],
        "software": [
            "deb", "exe", "dmg", "pkg", "iso", "img", "apk", "rpm", "pat", "flatpakref", "ova"
        ],
        "scripts": [
            "sh"
        ],
        "projects": [
            "xcf", "reason", "xoj", "aseprite", "yyz"
        ],
        "fonts": [
            "ttf", "otf", "woff", "woff2", "eot", "ttc", "fon", "fnt", "pfb", "pfm", "afm", "dfont"
        ],
        "configuration": [
            "json", "so", "ovpn", "gimp", "pal"
        ],
    }

    default_user_settings = {
        "theme": Theme.PRESETS[Theme.DEFAULT_PRESET],
        "source_folders": ["/path/to/folder/to/sort"],
        "destination_folder": "/path/to/destination/folder",
        "remove_duplicates_folders": ["/path/to/folder/to/process"],
        "preserve_folder_tree": False,
        "keep_original_files": True,
        "delete_empty_source_folders": False,
        "preview_before_sorting": True,
        "binary_search": True,
        "binary_search_large_files": False,
        "log_output_in_file": True,
        "check_for_updates_on_startup": True,
        "ask_before_removing_duplicates": True,
        "ask_before_removing_empty_folders": True,
        "binary_comparison_large_files_threshold": 5000000,
    }

    renamed_user_settings = {
        "folder_to_process": "source_folders",
        "remove_duplicates_folder": "remove_duplicates_folders",
    }

    folder_list_user_settings = (
        "source_folders",
        "remove_duplicates_folders",
    )

    legacy_theme_colors = {
        "color1": "background",
        "color2": "surface",
        "color3": "elevated",
        "color4": "text",
    }
