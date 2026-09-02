from src.application.component.SMSButton import SMSButton
from src.application.component.SMSButtonContainer import SMSButtonContainer
from src.application.component.SMSColorPicker import SMSColorPicker
from src.application.component.SMSSection import SMSSection
from src.application.service.EventManager import EventManager
from src.application.service.ThemeProvider import ThemeProvider
from src.application.view.SMSView import SMSView
from src.domain.entity.Theme import Theme


class AppearanceView(SMSView):
    """Palette editor. Every change is saved and applied to the whole interface at once."""

    def __init__(
        self,
        container,
        theme_provider: ThemeProvider,
        event_manager: EventManager,
    ):
        self.theme_provider = theme_provider

        super().__init__(container, theme_provider, event_manager)

        self.create_view()

    def create_view(self):
        self.render_title("Appearance", "Pick a preset, then fine tune any color.")

        self.render_sections([
            self.__create_presets_section,
            self.__create_colors_section,
        ])

    def __create_presets_section(self, container) -> SMSSection:
        section = SMSSection(container, self.theme, "Presets")

        presets = SMSButtonContainer(container=section.get_body(), theme=self.theme, direction="horizontal")
        presets.set_buttons([
            SMSButton(
                container=presets,
                theme=self.theme,
                text=preset_name,
                variant="primary" if self.__is_current_preset(preset_name) else "ghost",
                width=len(preset_name) + 2,
                command=lambda preset_name=preset_name: self.theme_provider.apply_preset(preset_name),
            )
            for preset_name in Theme.PRESETS
        ])
        presets.grid(row=0, column=0, sticky="w")

        return section

    def __create_colors_section(self, container) -> SMSSection:
        section = SMSSection(container, self.theme, "Colors")
        body = section.get_body()

        for row, (color_name, label) in enumerate(Theme.EDITABLE_COLORS.items()):
            SMSColorPicker(
                container=body,
                theme=self.theme,
                label=label,
                color=getattr(self.theme, color_name),
                on_pick=lambda color, color_name=color_name: self.theme_provider.save_color(color_name, color),
            ).grid(row=row, column=0, sticky="w", pady=6)

        SMSButton(
            container=body,
            theme=self.theme,
            text="Reset to the default palette",
            variant="ghost",
            width=28,
            command=lambda: self.theme_provider.apply_preset(Theme.DEFAULT_PRESET),
        ).grid(row=len(Theme.EDITABLE_COLORS), column=0, sticky="w", pady=(18, 0))

        return section

    def __is_current_preset(self, preset_name: str) -> bool:
        return self.theme.as_dict() == Theme(Theme.PRESETS[preset_name]).as_dict()
