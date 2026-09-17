from math import ceil


class Pagination:
    """Which slice of a result list is on screen, and the sentence describing it.

    A preview draws one card per file, and a card is a handful of widgets: a folder
    holding tens of thousands of files would be hundreds of thousands of them, built one
    at a time on the only thread Tk has. The window stops painting for the whole of it,
    and what comes out is a list nobody can aim a scrollbar at. Only the page on screen
    is ever built, so showing a result costs the same whether the analysis found forty
    files or forty thousand.

    It holds no widget and knows no card: the arithmetic is here so it can be tested
    without a window, and SMSPager draws what it says.
    """

    PAGE_SIZE = 50

    def __init__(self, total: int, page_size: int = PAGE_SIZE):
        self.total = max(0, total)
        self.page_size = max(1, page_size)
        self.page = 1

    def pages(self) -> int:
        """Never zero: an empty result is still the first page, so nothing has to guard
        against a page number the buttons could not move away from."""
        return max(1, ceil(self.total / self.page_size))

    def go_to(self, page: int):
        """Clamped rather than refused, so a step past either end is a no-op and the
        pager has no arithmetic of its own to get wrong."""
        self.page = min(max(page, 1), self.pages())

    def page_of(self, items: list) -> list:
        return items[self.first_index():self.first_index() + self.page_size]

    def first_index(self) -> int:
        return (self.page - 1) * self.page_size

    def first_shown(self) -> int:
        return 0 if self.total == 0 else self.first_index() + 1

    def last_shown(self) -> int:
        return min(self.first_index() + self.page_size, self.total)

    def has_previous(self) -> bool:
        return self.page > 1

    def has_next(self) -> bool:
        return self.page < self.pages()

    def summary(self) -> str:
        """The line between the two buttons. It doubles as the count of what the
        analysis found, which no other part of the screen keeps on display."""
        results = f"{self.total:,} result" + ("" if self.total == 1 else "s")

        if self.pages() == 1:
            return f"Showing all {results}"

        return (
            f"Showing {self.first_shown():,}-{self.last_shown():,} of {results}"
            f"  ·  page {self.page:,} of {self.pages():,}"
        )
