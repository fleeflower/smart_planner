import heapq
from datetime import datetime, timedelta
from data_structure.Task import Task
import datetime
from data_structure import Task, TimeList, TimeList as tl
import TaskInput as ti
import PrioritySorter as ps


"""
智能时间分配引擎核心模块
"""


class PomodoroAllocator:
    """
    默认策略：基于番茄钟的分配
    """

    def __init__(self, cycle: int = 45, min_chunk: int = 25):
        self.cycle = cycle
        self.min_chunk = min_chunk

    def split_task(self, task: Task) -> list[Task]:
        """
        拆分任务为番茄钟块
        param task: 待拆分的任务
        return: 番茄钟块列表
        """
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

        split_list = []
        split_time = task.start
        for chunk in chunks:
            split_time += timedelta(minutes = chunk)
            split_list.extend(task.split(split_time))
        
        return list(set(split_list))
        

class DayTimeEngine:
    """分配引擎核心"""

    def __init__(self,day):
        self.task_list = []
        self.class_table = []
        self.day = day
        
        self.register_slots()
        self.slots = self._init_free_slots()
        self.unallocated_tasks = []


    def register_slots(self):
        """
        得到任务输入
        :return:
        """
        self.class_table = ti.get_class_list().copy()
        self.task_list = ti.get_task_list().copy()


    def _init_free_slots(self) -> tl.TimeList:
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
    def _smart_split(task: Task, free_slots):
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
    def _resolve_dependencies(task_list: list[Task], priority: dict):
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

    def allocate(self, free_slots: tl.TimeList = None, task_list: list[Task] = None):
        """时间分配核心算法"""
        if not free_slots:
            free_slots = self.slots
        if not task_list:
            task_list = self.task_list
        # 阶段1：处理依赖关系并排序
        try:
            priority_weights = ps.get_priority(task_list) # 示例优先级计算
            ordered_tasks = self._resolve_dependencies(task_list, priority_weights)
        except ValueError as e:
            print(f"依赖解析失败: {str(e)}")
            return [], task_list  # 返回空分配和全部未分配任务

        # 阶段2：准备可分配时间槽（按开始时间排序）
        allocated = []
        unallocated = []

        # 阶段3：动态分配主循环
        for task in ordered_tasks:
            # 智能任务拆分（考虑当前剩余时间段）
            suitable_slots = TimeList.TimeList([s for s in free_slots if s.duration >= task.duration and (not task.deadline or s.end <= task.deadline)])
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

                if best_slot is not None:
                    # 找到合适的时间槽
                    selected_slot = free_slots.pop(best_slot)
                    selected_slot,remain_slot = selected_slot.split(selected_slot.start+timedelta(minutes=sub_task.duration))
                    selected_slot.replace(sub_task)
                    allocated.append(sub_task)
                    free_slots+=remain_slot
                else:
                    unallocated.append(sub_task)

        return allocated, unallocated
    
    def renew_list(self,cover = True):
        """
        当日程链表更新后采用次函数更新所有类列表
        会直接覆盖未分配任务列表
        :return: 
        """
        new_task_list = []
        new_free_slots = []
        for mt in self.day:
            if mt.time_type == "free":
                if mt.next.time_typr == "free":
                    mt.merge(mt.next)
                new_free_slots.append(mt)
            if mt.time_type == "task":
                new_task_list.append(mt.task)
        if cover:
            if len(self.unallocated_tasks)>0:
                raise ValueError("cannot cover with unallocated tasks")
            else:
                self.task_list = new_task_list
                self.slots = tl.TimeList(new_free_slots)
        return new_task_list,tl.TimeList(new_free_slots)
        
    def add_task(self, task: Task):
        """
        添加任务到日程表
        :param task:
        :return:
        """
        self.task_list.append(task)
        _,self.unallocated = self.allocate(task_list=[task],free_slots=self.slots)

    def remove_task(self, task: Task):
        """
        从日程表移除任务
        :param task:
        :return:
        """
        self.task_list.remove(task)
        for mt in self.day:
            if mt == task:
                new_node =  tl.Time(task.start, task.end, time_type="free")
                mt.replace(new_node)
                self.slots.append(new_node)
                if new_node.next and new_node.next.time_type == "free":
                    self.slots.merge(new_node,new_node.next)
                if new_node.front and new_node.front.time_type == "free":
                    self.slots.merge(new_node.front,new_node)
                break

    def modify_task(self, task: Task, **kwargs):
        """
        修改任务信息
        :param task:
        :param kwargs:
        :return:
        """
        pass





                
        


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