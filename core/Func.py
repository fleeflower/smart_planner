import datetime
import Task
import TimeList as tl
import TaskInput as ti
def get_task_input():
    """
    得到任务输入
    :return:
    """
    classtable = ti.get_class_list()
    task_list = ti.get_task_list()
    return classtable, task_list

def init_day(DAY_START: datetime.datetime, DAY_END: datetime.datetime,day_name:str)->tl.BassTime:
    """
    初始化一天的课表
    :param DAY_START: 开始时间
    :param DAY_END: 结束时间
    :param day_name: 星期几
    :return:
    """
    day_time = tl.Time(DAY_START, DAY_END,time_type="free")
    day = tl.BassTime(day_name,[day_time])
    return day

def init_free_slots(day: tl.BassTime,class_list: list[Task]):
    """
    初始化空闲时间
    切割一日
    :param day:
    :param class_list:
    :return:
    """
    day_time = tl.TimeList([item for item in day])
    class_table = tl.BassTime("class_list",class_list)
    for class_ in class_table:
        i = day_time.split(class_.start)
        j = day_time.split(class_.end)
        if j-i == 1:
            day_time.replace(class_,index = j)
        else:
            raise ValueError("class device failed")
    return tl.TimeList([time for time in day_time if time.time_type == "free"])