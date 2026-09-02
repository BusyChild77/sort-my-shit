class Version:
    """A released version, comparable to another one.

    `CURRENT` is the version of the running build. It keeps the development value in the
    sources and is stamped by the release workflow, so a build that was never released
    never believes itself to be a released one.
    """

    DEVELOPMENT = "0.0.0"
    CURRENT = "0.0.0"  # stamped at build time, see .github/workflows/release.yml

    NUMBERS = 3

    def __init__(self, name: str):
        self.name = (name or "").strip().lstrip("vV")
        self.numbers = self.__parse(self.name)

    @classmethod
    def current(cls) -> "Version":
        return cls(cls.CURRENT)

    def is_development(self) -> bool:
        return self.numbers == (0, 0, 0)

    def is_newer_than(self, other: "Version") -> bool:
        return self.numbers > other.numbers

    def __str__(self) -> str:
        return "v" + ".".join(str(number) for number in self.numbers)

    @classmethod
    def __parse(cls, name: str) -> tuple:
        """Anything unreadable reads as 0, so a malformed tag never looks like an update."""
        numbers = [cls.__leading_number(part) for part in name.split(".")[:cls.NUMBERS]]

        return tuple(numbers + [0] * (cls.NUMBERS - len(numbers)))

    @staticmethod
    def __leading_number(part: str) -> int:
        digits = ""

        for character in part:
            if not character.isdigit():
                break
            digits += character

        return int(digits) if digits else 0
