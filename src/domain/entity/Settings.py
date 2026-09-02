from src.domain.entity.Theme import Theme


class Settings:
    default_type_mapping = {
        "docs": [
            "pdf", "pdf_lbk", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
            "txt", "odt", "ods", "odp"
        ],
        "pics": [
            "jpg", "jpg_lbk", "jpeg", "jpeg_lbk", "png", "gif", "webp"
        ],
        "compressed": [
            "zip", "rar", "tar", "gz", "7z", "xz", "bz2"
        ],
        "audio": [
            "mp3", "wma", "wav", "flac", "ogg", "m4a", "m4a_lbk", "aac"
        ],
        "video": [
            "m4v", "webm", "mp4", "avi", "mkv", "flv", "mov", "wmv"
        ],
        "software": [
            "deb", "exe", "dmg", "pkg", "iso", "img", "apk", "rpm", "pat"
        ],
        "configuration": [
            "json", "so", "ovpn"
        ],
    }

    default_user_settings = {
        "theme": Theme.PRESETS[Theme.DEFAULT_PRESET],
        "source_folders": ["/path/to/folder/to/sort"],
        "destination_folder": "/path/to/destination/folder",
        "remove_duplicates_folder": "/path/to/destination/folder",
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

    # Settings renamed since version 1: {legacy name: current name}
    renamed_user_settings = {
        "folder_to_process": "source_folders",
    }

    # Flat theme colors used before the "theme" setting: {legacy name: theme color}
    legacy_theme_colors = {
        "color1": "background",
        "color2": "surface",
        "color3": "elevated",
        "color4": "text",
    }
