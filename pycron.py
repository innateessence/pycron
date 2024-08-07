#!/usr/bin/env python

import enum
from collections.abc import Callable
from time import sleep
import threading
from datetime import datetime, timedelta


class ScheduleTime:
    """

    ScheduleTime is a helper class to create a datetime object from a string


    usage:
        ScheduleTime.next_tick("5m") # returns a datetime object 5 minutes from now
    """

    @staticmethod
    def next_tick(until: str) -> datetime:
        time_map = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days",
            "w": "weeks",
        }

        if until is None:
            return datetime(year=9999, month=12, day=31, hour=23, minute=59, second=59)
        time_unit = until[-1]
        if time_unit not in time_map:
            raise ValueError("Invalid time unit")
        time_unit = time_map[time_unit]
        time_value = int(until[:-1])
        delta = timedelta(**{time_unit: time_value})
        until_time = datetime.now() + delta
        return until_time


class CronTime:
    """CronTime is a class to represent a crontime string  as a python object and provide methods to work with it"""

    def __init__(self, crontime_str: str):
        # TODO: Add seconds support?
        # TODO: Make Day of Week 0-7 (0 is Sunday) instead of 0-6 (0 is Monday) ??
        """
        Args:
            crontime:  crontime string in the format of * * * * * (minute hour day month weekday)
            * - Minute (0-59)
            * - Hour (0-23)
            * - Day of Month (1-31)
            * - Month (1-12)
            * - Day of Week (0-6) (0 is Monday)

        We do not currently support the / operator, such as */5 * * * * to run every 5 minutes
        We also do not currently support the - operator, such as 0-5 * * * * to run every minute from 0 to 5
        We also do not currently support the , operator, such as 0,5 * * * * to run at 0 minutes and 5 minutes

        Instead, you should just create multiple cron jobs.
        This may be added in the future
        """
        self._aliases = {
            "@midnight": "0 0 * * *",
            "@yearly": "0 0 1 1 *",
            "@annually": "0 0 1 1 *",
            "@monthly": "0 0 1 * *",
            "@weekly": "0 0 * * 0",
            "@daily": "0 0 * * *",
            "@hourly": "0 * * * *",
            "@minutely": "* * * * *",
        }
        self._unsupported_aliases = [
            "@boot",
            "@wakeup",
        ]

        self._crontime_str = crontime_str
        self.crontime = self._parse_crontime(crontime_str)
        self.next_runtime = self.now()

    def _parse_crontime(
        self, crontime: str
    ) -> tuple[int | str, int | str, int | str, int | str, int | str]:
        if crontime in self._aliases.keys():
            crontime = self._aliases[crontime]
        minute, hour, day, month, weekday = [
            int(i) if i.isdigit() else i for i in crontime.split(" ")
        ]
        return minute, hour, day, month, weekday

    @staticmethod
    def now() -> datetime:
        """
        datetime.now() without seconds or microseconds for comparison convenience reasons
        """
        retval = datetime.now()
        retval = retval.replace(microsecond=0)
        retval = retval.replace(second=0)
        return retval

    @classmethod
    def epoch(cls) -> int:
        """
        CronTime.now() as a unix epoch timestamp (int)
        """
        return int(cls.now().timestamp())

    def is_valid_tick(self, tick: datetime, now: datetime) -> bool:
        minute, hour, day, month, weekday = self.crontime

        if tick.minute != minute and minute != "*":
            return False
        if tick.hour != hour and hour != "*":
            return False
        if tick.day != day and day != "*":
            return False
        if tick.month != month and month != "*":
            return False
        if tick.weekday() != weekday and weekday != "*":
            return False

        tick.replace(second=0)
        tick.replace(microsecond=0)
        if tick <= now:
            return False
        return True

    def assign_static(self, dt: datetime) -> datetime:
        minute, hour, day, month, weekday = self.crontime
        if weekday != "*":
            weekday = int(weekday)
            while dt.weekday() != weekday:
                dt -= timedelta(days=1)
        if month != "*":
            month = int(month)
            dt = dt.replace(month=month)
        if day != "*":
            day = int(day)
            dt = dt.replace(day=day)
        if hour != "*":
            hour = int(hour)
            dt = dt.replace(hour=hour)
        if minute != "*":
            minute = int(minute)
            dt = dt.replace(minute=minute)
        dt = dt.replace(second=0)
        dt = dt.replace(microsecond=0)
        return dt

    def next_tick(self, now) -> datetime:
        dt = self.assign_static(now)
        while not self.is_valid_tick(dt, now):
            # TODO: This is not efficient
            # we should identify the largest time unit that we can increment by
            dt += timedelta(minutes=1)
        return dt

    def sleep_time_to_next_tick(self, next_tick: datetime) -> float:
        """calculates the amount of seconds between the two datetimes"""
        return next_tick.timestamp() - datetime.now().timestamp()

    def __str__(self) -> str:
        return " ".join(str(i) for i in self.crontime)

    def __repr__(self) -> str:
        return f"<CronTime: {self.__str__()}"


class CronJobStatus(enum.Enum):
    SLEEPING = "sleeping"
    RUNNING = "running"
    FAILED = "failed"


class CronJob(threading.Thread):
    def __init__(self, crontime: str, func, *args, **kwargs):
        # NOTE: switch `crontime` to Any object which provides a `next_tick` method to generate the next datetime object
        super().__init__()
        self.crontime = CronTime(crontime)
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.daemon = True
        self._status = CronJobStatus.SLEEPING
        self._last_run_time = None

    def run(self) -> None:
        while True:
            now = self.crontime.now()
            next_runtime = self.crontime.next_tick(now)
            sleep_time = self.crontime.sleep_time_to_next_tick(next_runtime)

            print("now:", now)
            print("next_runtime:", next_runtime)
            print(f"Sleeping for {round(sleep_time, 2)} seconds")

            self._status = CronJobStatus.SLEEPING
            sleep(sleep_time)
            self._status = CronJobStatus.RUNNING
            try:
                self.func(*self.args, **self.kwargs)
                self._last_run_time = self.crontime.now()
            except Exception as e:
                self._status = CronJobStatus.FAILED
                raise e

    def __repr__(self):
        return f"<CronJob: {self.func.__name__}({', '.join(str(arg) for arg in self.args)})>"


class PyCron:
    """
    example usage:
        pc = PyCron()

        def my_print(x):
            print(x)

        pc.add("* * * * *", my_print, "foo")
        pc.start()
        # wait until your systems clock reaches 00 seconds
        > foo
    """

    def __init__(self):
        self.cronjobs = []

    def add(self, crontime: str, func: Callable, *args, **kwargs):
        cronjob = CronJob(crontime, func, *args, **kwargs)
        self.cronjobs.append(cronjob)

    def start(self):
        for cronjob in self.cronjobs:
            cronjob.start()

    def stop(self):
        for cronjob in self.cronjobs:
            cronjob.stop()


def interactive_cron_test_func(foo, bar="bar"):
    now = datetime.now()
    print(f"Interactive cron test func ran at {now}")
    print("foo:", foo)
    print("bar:", bar)


if __name__ == "__main__":
    now = CronTime.now()
    ct1 = CronTime("* * * * *")
    tick1 = ct1.next_tick(now)
    tick2 = ct1.next_tick(tick1)
    tick3 = ct1.next_tick(tick2)
    tick4 = ct1.next_tick(tick3)
    tick5 = ct1.next_tick(tick4)

    print(f"ct1: {ct1}  : {ct1.next_tick(now)}")
    print(f"ct1: {ct1}  : {ct1.next_tick(tick1)}")
    print(f"ct1: {ct1}  : {ct1.next_tick(tick2)}")
    print(f"ct1: {ct1}  : {ct1.next_tick(tick3)}")
    print(f"ct1: {ct1}  : {ct1.next_tick(tick4)}")
    print(f"ct1: {ct1}  : {ct1.next_tick(tick5)}")

    print("tick5", tick5)

    # ct2 = CronTime("55 * * * *")
    # ct3 = CronTime("04 12 * * *")
    # ct4 = CronTime("02 02 02 * *")
    # ct5 = CronTime("04 04 04 04 *")

    # # Test next_tick
    # now = ct1.now()
    # print(f"{ct1}   : {ct1.next_tick(now)}")
    # print(f"{ct2}  : {ct2.next_tick(now)}")
    # print(f"{ct3}  : {ct3.next_tick(now)}")
    # print(f"{ct4}   : {ct4.next_tick(now)}")
    # print(f"{ct5}   : {ct5.next_tick(now)}")

    # print("Testing interactive cron job")
    pc = PyCron()
    pc.add("* * * * *", interactive_cron_test_func, "foo", bar="baz")
    pc.start()

    while threading.active_count() > 0:
        sleep(1)
