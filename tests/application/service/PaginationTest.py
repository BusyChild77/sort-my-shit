from unittest import TestCase

from src.application.service.Pagination import Pagination


class PaginationTest(TestCase):
    """A preview builds one card per result, and an analysis over a big folder comes
    back with tens of thousands of them: what is checked here is that only a page worth
    of results is ever handed to the screen, and that no move can land on a page holding
    nothing while results are left to show."""

    def test_given_fewer_results_than_a_page_when_asking_for_the_pages_then_there_is_one(self):
        self.assertEqual(Pagination(12, page_size=50).pages(), 1)

    def test_given_no_result_at_all_when_asking_for_the_pages_then_there_is_still_one(self):
        """Page zero would be a page the buttons could not move away from."""
        self.assertEqual(Pagination(0).pages(), 1)

    def test_given_results_filling_a_page_exactly_when_asking_for_the_pages_then_there_is_no_empty_one(self):
        self.assertEqual(Pagination(100, page_size=50).pages(), 2)

    def test_given_results_spilling_over_a_page_when_asking_for_the_pages_then_the_rest_has_one(self):
        self.assertEqual(Pagination(101, page_size=50).pages(), 3)

    def test_given_a_huge_result_when_asking_for_the_first_page_then_only_a_page_of_cards_is_handed_over(self):
        """The whole point: forty thousand results cost the same as forty to show."""
        items = list(range(40000))

        self.assertEqual(Pagination(len(items), page_size=50).page_of(items), items[:50])

    def test_given_the_second_page_when_asking_for_its_items_then_the_slice_follows_the_first(self):
        items = list(range(120))
        pagination = Pagination(len(items), page_size=50)

        pagination.go_to(2)

        self.assertEqual(pagination.page_of(items), items[50:100])

    def test_given_the_last_page_when_asking_for_its_items_then_only_what_is_left_comes_back(self):
        items = list(range(120))
        pagination = Pagination(len(items), page_size=50)

        pagination.go_to(3)

        self.assertEqual(pagination.page_of(items), items[100:])

    def test_given_a_page_past_the_last_one_when_going_to_it_then_it_stops_on_the_last(self):
        pagination = Pagination(120, page_size=50)

        pagination.go_to(99)

        self.assertEqual(pagination.page, 3)

    def test_given_a_page_before_the_first_one_when_going_to_it_then_it_stops_on_the_first(self):
        pagination = Pagination(120, page_size=50)

        pagination.go_to(0)

        self.assertEqual(pagination.page, 1)

    def test_given_the_first_page_when_asking_what_it_can_move_to_then_only_the_next_one_is_offered(self):
        pagination = Pagination(120, page_size=50)

        self.assertFalse(pagination.has_previous())
        self.assertTrue(pagination.has_next())

    def test_given_the_last_page_when_asking_what_it_can_move_to_then_only_the_previous_one_is_offered(self):
        pagination = Pagination(120, page_size=50)

        pagination.go_to(3)

        self.assertTrue(pagination.has_previous())
        self.assertFalse(pagination.has_next())

    def test_given_a_single_page_of_results_when_asking_what_it_can_move_to_then_neither_is_offered(self):
        pagination = Pagination(12, page_size=50)

        self.assertFalse(pagination.has_previous())
        self.assertFalse(pagination.has_next())

    def test_given_a_page_in_the_middle_when_reading_its_summary_then_it_names_the_range_it_shows(self):
        pagination = Pagination(1234, page_size=50)

        pagination.go_to(2)

        self.assertEqual(pagination.summary(), "Showing 51-100 of 1,234 results  ·  page 2 of 25")

    def test_given_the_last_page_when_reading_its_summary_then_it_stops_at_the_last_result(self):
        pagination = Pagination(1234, page_size=50)

        pagination.go_to(25)

        self.assertEqual(pagination.summary(), "Showing 1,201-1,234 of 1,234 results  ·  page 25 of 25")

    def test_given_a_single_page_when_reading_its_summary_then_it_is_the_count_and_no_page_number(self):
        self.assertEqual(Pagination(12, page_size=50).summary(), "Showing all 12 results")

    def test_given_one_single_result_when_reading_the_summary_then_it_is_not_written_in_the_plural(self):
        self.assertEqual(Pagination(1).summary(), "Showing all 1 result")

    def test_given_a_page_size_of_nothing_when_paging_then_it_falls_back_on_one_result_a_page(self):
        """Nothing offers a zero, but a page holding no result is an endless list of
        empty pages, so the arithmetic refuses it rather than the caller."""
        pagination = Pagination(3, page_size=0)

        self.assertEqual(pagination.pages(), 3)

    def test_given_a_default_pagination_when_reading_its_size_then_it_is_the_shared_page_size(self):
        self.assertEqual(Pagination(1000).page_of(list(range(1000))), list(range(Pagination.PAGE_SIZE)))
