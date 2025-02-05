from datetime import datetime, timedelta, time
from main import config
from data_structure import Task, TimeList, TimeList as tl

class day:
    def __init__(self, day_name):
        self.day_name = day_name
        self.day = None
        self._init_day(config.DAY_START, config.DAY_END)

    def _init_day(self, DAY_START: datetime.time, DAY_END: datetime.time) -> tl.BassTime:
        """
        初始化一天的课表
        :param DAY_START: 常量一日的开始时间
        :param DAY_END: 常量一日的结束时间
        :return:
        """
        day_time = tl.Time(DAY_START, DAY_END, time_type="free")
        self.day = tl.BassTime(self.day_name, [day_time])
