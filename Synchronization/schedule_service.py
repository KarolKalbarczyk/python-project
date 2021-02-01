import re

from injector import inject

from Synchronization import synchronization_service
from apscheduler.schedulers.blocking import BlockingScheduler

from Synchronization.synchronization_service import SynchronizationService


class ScheduleService():

    @inject
    def __init__(self, synchornizationService : SynchronizationService):
        self.__synchronizationService = synchornizationService
        self.__scheduler = BlockingScheduler()
        self.id = "id"
        self.hasJob = False
        self.isRunning = False

    def stop_job(self):
        if self.hasJob:
            self.__scheduler.remove_job(self.id)
            self.hasJob = False

    def get_schedule(self, string):
        if string is None:
            return None

        def get_permitted_digits(index):
            if index == 0:
                return 4
            elif index == 4:
                return 1
            else:
                return 2

        regex = lambda d: r"(\*|(\d{%d}(,|-)?))*" % d
        qualifiers = string.split(' ')
        if len(qualifiers) != 8:
            return None

        for i in range(0, len(qualifiers)):
            if not re.match(regex(get_permitted_digits(i)), qualifiers[i]):
                return None

        return {
            'year': qualifiers[0],
            'month': qualifiers[1],
            'week': qualifiers[2],
            'day': qualifiers[3],
            'day_of_week': qualifiers[4],
            'hour': qualifiers[5],
            'minute': qualifiers[6],
            'second': qualifiers[7],
        }

    def start_job(self, schedule):
        self.stop_job()
        self.__scheduler.add_job(
            self.__synchronizationService.synchronize,
            'cron',
            year = schedule['year'],
            month=schedule['month'],
            day= schedule['day'],
            day_of_week = schedule['day_of_week'],
            hour=schedule['hour'],
            minute=schedule['minute'],
            second=schedule['second'],
            id = self.id)

        self.hasJob = True
        if not self.isRunning:
            self.isRunning = True
            self.__scheduler.start()
