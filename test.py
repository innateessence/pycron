#!/usr/bin/env python3
from datetime import datetime, timedelta
from pycron import CronTime


def test1():
    crontime = CronTime("* * * * *")
    dt = datetime(2024, 3, 4, 23, 1, 0, 0)
    tick1 = crontime.next_tick(dt)
    tick2 = crontime.next_tick(tick1)
    tick3 = crontime.next_tick(tick2)
    tick4 = crontime.next_tick(tick3)
    tick5 = crontime.next_tick(tick4)

    expected_tick_1 = dt + timedelta(minutes=1)
    expected_tick_2 = dt + timedelta(minutes=2)
    expected_tick_3 = dt + timedelta(minutes=3)
    expected_tick_4 = dt + timedelta(minutes=4)
    expected_tick_5 = dt + timedelta(minutes=5)

    assert tick1 == expected_tick_1
    assert tick2 == expected_tick_2
    assert tick3 == expected_tick_3
    assert tick4 == expected_tick_4
    assert tick5 == expected_tick_5
    print("[Test 1] Passed!")


def test2():
    crontime = CronTime("@minutely")
    dt = datetime(2024, 3, 4, 23, 1, 0, 0)
    tick1 = crontime.next_tick(dt)
    tick2 = crontime.next_tick(tick1)
    tick3 = crontime.next_tick(tick2)
    tick4 = crontime.next_tick(tick3)
    tick5 = crontime.next_tick(tick4)

    expected_tick_1 = dt + timedelta(minutes=1)
    expected_tick_2 = dt + timedelta(minutes=2)
    expected_tick_3 = dt + timedelta(minutes=3)
    expected_tick_4 = dt + timedelta(minutes=4)
    expected_tick_5 = dt + timedelta(minutes=5)

    assert tick1 == expected_tick_1
    assert tick2 == expected_tick_2
    assert tick3 == expected_tick_3
    assert tick4 == expected_tick_4
    assert tick5 == expected_tick_5
    print("[Test 2] Passed!")


def Main():
    test1()
    test2()


if __name__ == "__main__":
    Main()
