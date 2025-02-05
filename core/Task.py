import datetime
from TimeList import Time

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
        super().__init__(start=None, end=None)
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

    def remaining_time(self, current_time: datetime):
        """
        计算任务的剩余时间。

        :param current_time: 当前时间。
        :return: 如果任务有截止日期，则返回剩余时间，否则返回None。
        """
        if self.deadline:
            return self.deadline - current_time//datetime.timedelta(hours=1)
        return None

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