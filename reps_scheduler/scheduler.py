"""
This module contains functions to create exercise schedules based on set goals
and current ability.
"""
import itertools
import math
import typing

import more_itertools


def peak_in_middle_function(x: float) -> float:
    """
    Return f(x) where
        f(x) = {2x-2, x<=2
               {6-2x, 2<x
    to describe ideal 5 set:
        [18, 20, 22, 20, 18] ~ [-2, 0, 2, 0, -2]
    """
    # pylint: disable=C0103
    piecewise_edge = 2
    if x <= piecewise_edge:
        return 2 * x - 2
    return 6 - 2 * x


def peak_toward_front_function(x: float) -> float:
    """
    Return f(x) where
        f(x) = {2x, x<=2
               {12-4x, 2<x
    to describe ideal 5 set:
        [20, 22, 24, 20, 16] ~ [0, 2, 4, 0, -4]
    """
    # pylint: disable=C0103
    piecewise_edge = 2
    if x <= piecewise_edge:
        return 2 * x
    return 12 - 4 * x


def front_load_function(x: float) -> float:
    """
    Return f(x) where
        f(x) = {8-x, x<1
               {4-2x, 1<=x
    to describe ideal 5 set:
        [28, 22, 20, 18, 12] ~ [8, 2, 0, -2, -8]
    """
    # pylint: disable=C0103
    piecewise_edge = 1
    if x < piecewise_edge:
        return 8 - x
    return 4 - 2 * x


DISTRO_SHAPE_FUNCTIONS = [
    peak_in_middle_function,
    peak_toward_front_function,
    front_load_function,
]


def argmax(values: list):
    """Return first index of maximum value."""
    # replace with np.argmax if there's ever a reason to import numpy anyway
    return values.index(max(values))


def schedule_by_shape(
    distro_shape: typing.Callable[[float], float], num_set: int, total: int
) -> list[int]:
    """
    Return a list of num_set counts that sum to the given total and roughly
    approximate something a given distribution shape function.
    """
    if num_set <= 0 or total < 0:
        raise ValueError(
            "requires at least one set and a non-negative number of total reps"
        )
    if not isinstance(num_set, int) or not isinstance(total, int):
        raise ValueError("requires integer inputs for number of sets and total reps")

    # avoid division by zero
    if num_set == 1:
        return [total]

    x_values = (i * 4 / (num_set - 1) for i in range(num_set))
    unscaled_diffs_from_average = [distro_shape(x) for x in x_values]

    set_average = total / num_set
    diff_scale = set_average / 20
    diffs_from_average = [diff_scale * diff for diff in unscaled_diffs_from_average]
    sets = [round(diff + set_average) for diff in diffs_from_average]

    # fix any rounding errors.
    rounding_error = total - sum(sets)
    if rounding_error < 0:
        sets[-1] += rounding_error
    else:
        sets[argmax(sets)] += rounding_error

    return sets


def day1_schedule(num_set: int, total: int) -> list[int]:
    """Day 1 wrapping for schedule_by_shape."""
    return schedule_by_shape(peak_in_middle_function, num_set, total)


def day2_schedule(num_set: int, total: int) -> list[int]:
    """Day 2 wrapping for schedule_by_shape."""
    return schedule_by_shape(peak_toward_front_function, num_set, total)


def day3_schedule(num_set: int, total: int) -> list[int]:
    """Day 3 wrapping for schedule_by_shape."""
    return schedule_by_shape(front_load_function, num_set, total)


DAY_SCHEDULES = [day1_schedule, day2_schedule, day3_schedule]
N_SETS = 5
RATIO_OF_MAX_FOR_N_SETS = 0.6
DAY_INCREASES = [1.13, 1.10, 1.10]
DAYS_PER_WEEK = len(DAY_INCREASES)
WEEKLY_INCREASE = math.prod(DAY_INCREASES)


def get_total_increase_after_days(num_days):
    """
    Return the increase after the given number of days. Since the percent
    increase differs by day, can't do this with simple exponential function.
    """
    endless_increases = itertools.cycle(DAY_INCREASES)
    return math.prod(more_itertools.take(num_days, endless_increases))


def get_progression(starting_max, single_set_goal):
    """
    Return the an exercise schedule where the total increases by a set amount
    determined by which day of the week it is.
    """
    n_sets = N_SETS
    starting_average = RATIO_OF_MAX_FOR_N_SETS * starting_max
    est_required_inc = single_set_goal / starting_average
    # after n weeks, increase by (WEEKLY_INCREASE)^n.
    # direct calculation with generator seems better for readability
    # but not probably not efficiency.
    est_weeks = math.ceil(math.log(est_required_inc) / math.log(WEEKLY_INCREASE))

    starting_total = round(starting_average * n_sets)
    schedule = (
        DAY_SCHEDULES[day % DAYS_PER_WEEK](
            n_sets, round(get_total_increase_after_days(day) * starting_total)
        )
        for day in range(DAYS_PER_WEEK * est_weeks)
    )

    schedule = itertools.takewhile(lambda day: max(day) < single_set_goal, schedule)
    return [*list(schedule), [single_set_goal]]
