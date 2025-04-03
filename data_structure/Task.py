import datetime
from datetime import datetime, timedelta, time
from logging import NullHandler

from data_structure.TimeList import Time

URGENCY_MAP = {
    'critical': 5,  # 紧急且重要
    'high': 4,
    'medium': 3,
    'low': 2,
    'optional': 1  # 可选任务
}

class Task(Time):
    def __init__(self, name: str, duration: int, deadline: datetime = None,
                 urgency: str = None, splittable: bool = False, reducible: bool = False,
                 prerequisites: list = None, task_id: str = None):
        """
        初始化一个任务对象。

        :param name: 任务的名称。
        :param duration: 任务的持续时长。
        :param task_id: 任务的唯一标识符（可选）。
        :param deadline: 任务的截止日期（可选）。
        :param urgency: 任务的主观紧急状态（可选）。
        :param splittable: 任务是否可拆分。
        :param reducible: 任务是否可缩短。
        :param prerequisites: 任务的前置任务列表（可选）。
        """
        super().__init__(start=None, end=None,time_type='task')
        self.name = name
        self.id = task_id
        self.duration = duration
        self.deadline = deadline
        self.urgency = urgency
        self.splittable = splittable
        self.reducible = reducible
        self.prerequisites = prerequisites if prerequisites else []
        self.completed = False

    def add_prerequisite(self, task: 'Task'):
        """
        添加一个前置任务。

        :param task: 要添加为前置任务的任务对象。
        """
        self.prerequisites.append(task)

    def mark_completed(self):
        """
        将任务标记为已完成。
        """
        self.completed = True

    def is_overdue(self, current_time: datetime) -> bool:
        """
        检查任务是否已过期。

        :param current_time: 当前时间。
        :return: 如果任务已过期且未完成，则返回True，否则返回False。
        """
        return self.deadline and current_time > self.deadline and not self.completed

    def remaining_time(self):
        """
        计算任务的剩余时间。
        :return: 如果任务有截止日期，则返回剩余时间，否则返回None。
        """
        time_anchor = datetime.now()
        now = time_anchor or datetime.now()
        if self.deadline.tzinfo:
            anchor_time = now.astimezone(self.deadline.tzinfo)
        else:
            anchor_time = now.replace(tzinfo=None)

        delta = self.deadline - anchor_time
        remaining_min = delta.total_seconds() / 60
        return remaining_min

    def __str__(self):
        """
        返回任务的字符串表示。
        """
        status = "Completed" if self.completed else "Pending"
        return (f"Task(Name: {self.name}, Duration: {self.duration}, Deadline: {self.deadline}, "
                f"Urgency: {self.urgency}, Splittable: {self.splittable}, Reducible: {self.reducible}, "
                f"Prerequisites: {[task.name for task in self.prerequisites]}, Status: {status})")

    def __lt__(self,other):
        return self.priority<other.priority

class StaticTask(Time):
    """
    课程，包括开始时间，结束时间，以及具体日期或者循环周期（或特别的以周循环）
    """
    def __init__(self,start: datetime.time, end: datetime.time,name:str,other_detail:dict = None,start_date:datetime.date = datetime.today(),end_date:datetime.date = datetime.today(),circle:int = None,circle_in_week:int = None,is_fine_for_task:bool = False):
        super().__init__(start,end,time_type='StaticTask')
        self.name = name
        self.other_detail = other_detail
        self.start_date = start_date
        self.end_date = end_date
        self.circle = circle
        self.circle_in_week = circle_in_week
        self.is_fine_for_task = is_fine_for_task

    def __str__(self):
        return f"StaticTask(Name: {self.name}, Start: {self.start}, End: {self.end}, Start_date: {self.start_date}, End_date: {self.end_date}, Circle: {self.circle}, Circle_in_week: {self.circle_in_week}, Is_fine_for_task: {self.is_fine_for_task})"

