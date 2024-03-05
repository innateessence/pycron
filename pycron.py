#!/usr/bin/env python

from time import sleep
import threading
from datetime import datetime, timedelta


class CronTime:
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

        self._crontime_str = crontime_str
        self.crontime = self._parse_crontime(crontime_str)
        self.next_runtime = self.now()

    def _parse_crontime(self, crontime: str):
        if crontime in self._aliases.keys():
            crontime = self._aliases[crontime]
        minute, hour, day, month, weekday = [
            int(i) if i.isdigit() else i for i in crontime.split(" ")
        ]
        return minute, hour, day, month, weekday

    @staticmethod
    def now() -> datetime:
        retval = datetime.now()
        # retval.replace(microsecond=0)
        # retval.replace(second=0)
        return retval

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
        if tick <= now:
            return False
        return True

    def assign_static(self, dt: datetime):
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
        # TODO: increment by seconds?
        dt = self.assign_static(now)
        while not self.is_valid_tick(dt, now):
            dt += timedelta(minutes=1)
        return dt

    def __str__(self):
        return " ".join(str(i) for i in self.crontime)

    def __repr__(self):
        return f"<CronTime: {self.__str__()}"


class CronJob(threading.Thread):
    def __init__(self, crontime: str, func, *args, **kwargs):
        super().__init__()
        self.crontime = CronTime(crontime)
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.daemon = True

    def run(self):
        while True:
            now = self.crontime.now()
            next_runtime = self.crontime.next_tick(now)
            sleep_time = (next_runtime - datetime.now()).seconds
            print(f"Sleeping for {sleep_time} seconds")
            sleep(sleep_time)


class PyCron:
    """
    example usage:
        pc = PyCron()
        lambda print_foo: print("foo")
        pc.add("* * * * *", print_foo)
        pc.start()
    """

    def __init__(self):
        self.cronjobs = []

    def add(self, crontime, func, *args, **kwargs):
        cronjob = CronJob(crontime, func, *args, **kwargs)
        self.cronjobs.append(cronjob)

    def start(self):
        for cronjob in self.cronjobs:
            cronjob.start()

    def stop(self):
        for cronjob in self.cronjobs:
            cronjob.stop()


def interactive_cron_test_func():
    now = datetime.now()
    print(f"Interactive cron test func ran at {now}")


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
    # pc = PyCron()
    # pc.add("* * * * *", interactive_cron_test_func)
    # pc.start()

    # while threading.active_count() > 0:
    #     sleep(1)
