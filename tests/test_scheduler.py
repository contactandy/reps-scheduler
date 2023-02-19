"""Test routines from reps_scheduler.scheduler.py."""

import more_itertools
import pytest

from reps_scheduler import scheduler


def test_day1_schedule():
    """Test day1_schedule."""
    ideal = [18, 20, 22, 20, 18]
    assert scheduler.day1_schedule(len(ideal), sum(ideal)) == ideal


def test_day2_schedule():
    """Test day2_schedule."""
    ideal = [20, 22, 24, 20, 16]
    assert scheduler.day2_schedule(len(ideal), sum(ideal)) == ideal


def test_day3_schedule():
    """Test day3_schedule."""
    ideal = [28, 22, 20, 18, 12]
    assert scheduler.day3_schedule(len(ideal), sum(ideal)) == ideal


@pytest.fixture(name="num_set", params=range(1, 10))
def fixture_num_set(request):
    """Parametrized fixture for number of sets for day in exercise plan."""
    return request.param


@pytest.fixture(name="total", params=[25, 100, 203])
def fixture_total(request):
    """Parametrized fixture for sum of reps per exercise set."""
    return request.param


class TestScheduleByShape:
    """Test schedule_by_shape."""

    def test_output(self, num_set, total):
        """
        Test the output for various sanity checks.
        """
        for shape in scheduler.DISTRO_SHAPE_FUNCTIONS:
            counts = scheduler.schedule_by_shape(shape, num_set, total)
            assert sum(counts) == total
            assert all(isinstance(count, int) for count in counts)
            # enforce that final rep is easiest
            assert min(counts) == counts[-1]

    @pytest.mark.parametrize(
        "bad_input", [(-1, 10), (3, -1), (-1, -1), (0, 10), (4, 23.3), (5.5, 20)]
    )
    def test_catches_bad_input(self, bad_input):
        """Test that raises ValueError when given bad input."""
        for shape in scheduler.DISTRO_SHAPE_FUNCTIONS:
            set_num, total = bad_input
            with pytest.raises(ValueError):
                scheduler.schedule_by_shape(shape, set_num, total)


def test_get_total_increase_after_days():
    """
    Test get_total_increase_after_days.
    Note: test reliant on 3 days_per_week schedule.
    """
    day_increases = scheduler.DAY_INCREASES
    week1_inc = day_increases[0] * day_increases[1] * day_increases[2]
    week2_inc = week1_inc * day_increases[0] * day_increases[1] * day_increases[2]

    actual_day4_inc = scheduler.get_total_increase_after_days(4)
    assert actual_day4_inc == week1_inc * day_increases[0]

    actual_day8_inc = scheduler.get_total_increase_after_days(8)
    expected_day8_inc = week2_inc * day_increases[0] * day_increases[1]
    assert actual_day8_inc == expected_day8_inc


def test_get_progression():
    """Test get_progression."""
    starting_value = 10
    goal = 100
    schedule = scheduler.get_progression(starting_value, goal)

    for day in schedule:
        assert all(isinstance(rep, int) for rep in day)

    *training_days, final_day = schedule
    assert final_day == [goal]
    for one_day, next_day in more_itertools.pairwise(training_days):
        assert sum(one_day) < sum(next_day)
