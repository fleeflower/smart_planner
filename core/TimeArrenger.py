import heapq
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timedelta, time
from heapq import heappush, heappop
import TimeList
from core.Task import Task
import datetime
import Task
import TimeList as tl
import TaskInput as ti
import FuncTools
import PrioritySorter as ps


"""
智能时间分配引擎核心模块
"""

# 常量定义每日的开始和结束时间
TIME_START = datetime.time(6, 0)  # 6点
TIME_END = datetime.time(2, 0)

class AllocationStrategy(ABC):
    """策略模式抽象类（扩展点1）"""

    @abstractmethod
    def allocate(self,
                 task: TimeList,
                 sparetimes: TimeList):
        pass


class PomodoroAllocator(AllocationStrategy):
    """默认策略：基于番茄钟的分配"""

    def __init__(self, cycle: int = 45, min_chunk: int = 25):
        self.cycle = cycle
        self.min_chunk = min_chunk

    def _split_task(self, task: Task) -> list[Task]:
        """拆分任务为番茄钟块"""
        if not task.splitable:
            return [task]

        chunks = []
        remaining = task.duration

        while remaining > 0:
            chunk = min(remaining, self.cycle)
            if remaining - chunk < self.min_chunk and len(chunks) > 0:
                chunk = remaining  # 合并最后的小块
            chunks.append(chunk)
            remaining -= chunk

        return [
            Task(
                task_id=f"{task.task_id}_part{i + 1}",
                name=f"{task.name} (Part {i + 1})",
                duration=chunk,
                deadline=task.deadline,
                urgency=task.urgency,
                prerequisites= task.prerequisites if i == 0 else [f"{task.task_id}_part{i}"],
            )
            for i, chunk in enumerate(chunks)
        ]

    def allocate(self, tasks, slots):
        # 实现细节略，包含：
        # 1. 任务拆分
        # 2. 依赖解析
        # 3. 时间匹配
        # 4. 分配验证
        pass


class DayTimeEngine:
    """分配引擎核心"""

    def __init__(self,day_name: str, strategy: AllocationStrategy = None):
        self.strategy = strategy or PomodoroAllocator()
        self.task_list = []
        self.class_table = []
        self.day = None
        self.day_name = day_name

        self.register_slots()
        self.day = self.init_day(TIME_START, TIME_END)
        self.slots = self.init_free_slots()


    def register_slots(self):
        """
        得到任务输入
        :return:
        """
        self.class_table = ti.get_class_list()
        self.task_list = ti.get_task_list()

    def init_day(self,DAY_START: datetime.datetime, DAY_END: datetime.datetime) -> tl.BassTime:
        """
        初始化一天的课表
        :param DAY_START: 常量一日的开始时间
        :param DAY_END: 常量一日的结束时间
        :return:
        """
        day_time = tl.Time(DAY_START, DAY_END, time_type="free")
        self.day = tl.BassTime(self.day_name, [day_time])

    def init_free_slots(self):
        """
        初始化空闲时间
        切割一日
        :return:
        """
        day_time = tl.TimeList([item for item in self.day])
        class_table = tl.BassTime("class_list", self.class_table)
        for class_ in class_table:
            i = day_time.split(class_.start)
            j = day_time.split(class_.end)
            if j - i == 1:
                day_time.replace(class_, index=j)
            else:
                raise ValueError("class device failed")
        return tl.TimeList([time for time in day_time if time.time_type == "free"])

    @staticmethod
    def smart_split(task: Task, free_slots):
        """根据可用时间段动态拆分任务"""
        if not task.splitable:
            return [task]

        # 寻找可用的连续时间段
        suitable_slots = [s for s in free_slots if s.duration >= 25]
        if not suitable_slots:
            return [task]

        # 计算最佳拆分粒度
        max_chunk = max(s.duration for s in suitable_slots)
        chunks = []
        remaining = task.duration

        while remaining > 0:
            chunk_size = min(remaining, max_chunk)
            i = len(chunks)
            chunks.append(Task(
                task_id=f"{task.task_id}_part{i+ 1}",
                name=f"{task.name} (Part {i + 1})",
                duration=chunk_size,
                deadline=task.deadline,
                urgency=task.urgency,
                prerequisites= task.prerequisites if i == 0 else [f"{task.task_id}_part{i}"],
            ))
            remaining -= chunk_size

        return chunks

    @staticmethod
    def resolve_dependencies(task_list: list[Task], priority: dict):
        """处理任务依赖关系，按优先级返回可执行顺序"""
        task_map = {t.task_id: t for t in task_list}
        in_degree = {t.task_id: len(t.prerequisites) for t in task_list}
        ordered_tasks = []

        priority_queue = [(-priority[t.task_id], t.task_id) for t in task_list if in_degree[t.task_id] == 0]
        heapq.heapify(priority_queue)

        # 拓扑排序主逻辑
        while priority_queue:
            current_priority, current_task_id = heapq.heappop(priority_queue)
            ordered_tasks.append(task_map[current_task_id])

            for task in task_list:
                if current_task_id in task.prerequisites:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        heapq.heappush(priority_queue, (-priority[task.task_id], task.task_id))

        # 检查是否所有任务都被处理
        if len(ordered_tasks) != len(task_list):
            raise ValueError("存在循环依赖")

        return ordered_tasks

    def allocate(self):
        """优化后的时间分配核心算法"""
        # 阶段1：处理依赖关系并排序
        try:
            priority_weights = ps.get_priority(self.task_list) # 示例优先级计算
            ordered_tasks = self.resolve_dependencies(self.task_list, priority_weights)
        except ValueError as e:
            print(f"依赖解析失败: {str(e)}")
            return [], self.task_list  # 返回空分配和全部未分配任务

        # 阶段2：准备可分配时间槽（按开始时间排序）
        free_slots = tl.TimeList(self.slots.time_list, order="start")
        allocated = []
        unallocated = []

        # 阶段3：动态分配主循环
        for task in ordered_tasks:
            # 智能任务拆分（考虑当前剩余时间段）
            suitable_slots = TimeList.TimeList([s for s in free_slots if s.duration >= task.duration and  (not task.deadline or s.end <= task.deadline)])
            sub_tasks = self.smart_split(task,suitable_slots) if task.splitable else [task]

            for sub_task in sub_tasks:
                best_fit = None
                best_slot = None

                # 寻找最佳匹配时间段（满足以下条件）：
                # 1. 时间足够容纳任务
                # 2. 符合截止时间要求（如果有）
                # 3. 剩余空间最小（减少碎片）
                for slot in free_slots:
                    # 检查时间容量
                    if slot.duration < sub_task.duration:
                        continue

                    # 检查截止时间
                    if sub_task.deadline:
                        slot_end_time = datetime.datetime.combine(datetime.date.today(), slot.end)
                        if slot_end_time > sub_task.deadline:
                            continue

                    # 评估匹配质量
                    remaining = slot.duration - sub_task.duration
                    if best_fit is None or remaining < best_fit:
                        best_fit = remaining
                        best_slot = slot

                if best_slot != None:
                    # 找到合适的时间槽
                    selected_slot = free_slots.pop(best_slot)
                    selected_slot,_ = selected_slot.split(selected_slot.start+timedelta(minutes=sub_task.duration))
                    selected_slot.replace(sub_task)
                    allocated.append(sub_task)
                else:
                    unallocated.append(sub_task)

        return allocated, unallocated


# 扩展点示例（伪代码实现）
# class MLEnhancer:
#     """机器学习增强（扩展点4）"""
#
#     def predict_efficiency(self, task: Task, slot: TimeSlot) -> float:
#         """
#         预测用户在指定时间段执行任务的效率
#         返回：0.0-1.0之间的效率系数
#         """
#         # 伪代码：基于历史数据的时间段效率预测
#         return 0.8
#
#
# class DynamicAdjuster:
#     """动态调整器（扩展点5）"""
#
#     def reallocate(self,
#                    engine: TimeEngine,
#                    changed_tasks: List[Task]):
#         """
#         当任务状态变化时重新分配
#         :param changed_tasks: 发生变化的任务列表
#         """
#         # 伪代码：增量式重新分配逻辑
#         pass

