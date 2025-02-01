import datetime
class Node:
    """
    链表节点基类，包含前驱和后继节点的引用。
    """

    def __init__(self, front=None, next=None):
        self.front = front
        self.next = next

    def remove(self):
        """从链表中移除当前时间段。"""
        if self.front:
            self.front.next = self.next
        if self.next:
            self.next.front = self.front
        self.front = None
        self.next = None

    def replace(self, new_node):
        """替换当前节点为新节点。"""
        if self.front:
            self.front.next = new_node
        if self.next:
            self.next.front = new_node
        new_node.front = self.front
        new_node.next = self.next
        self.front = None
        self.next = None

class Time(Node):
    """
    表示一个时间段，包含开始时间、结束时间、类型及相邻节点引用。
    """

    def __init__(self, start: datetime, end: datetime, time_type: str = None, front: 'Time' = None, next: 'Time' = None):
        """
        初始化时间段。

        :param start: 开始时间。
        :param end: 结束时间。
        :param time_type: 时间段类型。
        :param front: 前驱节点。
        :param next: 后继节点。
        :raises ValueError: 如果开始时间大于结束时间。
        """
        if start > end:
            raise ValueError("Start time must be before end time")

        super().__init__(front, next)
        self.type = time_type
        self.start = start
        self.end = end
        self.duration = end - start

    def split(self, split_time: float) -> ('Time', 'Time'):
        """
        将当前时间段在指定时间点分割为两个相邻时间段。

        :param split_time: 分割时间点。
        :return: 分割后的两个时间段（前段和后段）。
        :raises ValueError: 如果分割时间点不在当前时间范围内。
        """
        if not self.start < split_time < self.end:
            raise ValueError("Split time must be within current time range")

        # 创建新时间段
        front_part = Time(self.start, split_time, self.type, self.front, None)
        back_part = Time(split_time, self.end, self.type, front_part, self.next)
        front_part.next = back_part

        # 更新原有相邻节点的连接
        if self.front:
            self.front.next = front_part
        if self.next:
            self.next.front = back_part

        return front_part, back_part


    def is_conflict(self) -> bool:
        """
        检查当前时间段是否与相邻时间段冲突。

        :return: 如果存在冲突返回 True，否则返回 False。
        """
        return not ((not self.front or self.start >= self.front.end) and
                    (not self.next or self.end <= self.next.start))

    def modify(self, **kwargs) -> None:
        """
        修改时间段的属性。

        :param kwargs: 要修改的属性和值。
        :raises ValueError: 如果修改后的时间与其他时间段冲突。
        """
        for key, value in kwargs.items():
            if key in ['start', 'end']:
                if key == 'start' and (
                        (self.next and value >= self.next.start) or (self.front and value < self.front.end)):
                    raise ValueError("Time conflict")
                if key == 'end' and (
                        (self.next and value > self.next.start) or (self.front and value <= self.front.end)):
                    raise ValueError("Time conflict")
            setattr(self, key, value)
        self.duration = self.end - self.start

    def __repr__(self):
        return f"Time({self.start}-{self.end}, {self.type})"


class SignTime(Node):
    """
    链表头节点，用于标识链表的开始。
    """

    def __init__(self, item, sign_type: str, front=None, next=None):
        self.sign_type = sign_type
        self.load = item
        super().__init__(front, next)


class BassTime:
    """
    链表队列，用于管理时间段节点。
    """

    def __init__(self, name, ls: list[Node]):
        """
        初始化链表队列。

        :param name: 链表名称。
        :param ls: 初始节点列表。
        """
        self.name = name
        self.head = SignTime(ls[0], name)
        self.tail = SignTime(ls[-1], name)
        for i in range(1, len(ls)):
            ls[i - 1].next = ls[i]
            ls[i].front = ls[i - 1]
            if i == 1:
                ls[i].front = self.head
            if i == len(ls) - 1:
                ls[i].next = self.tail

    def __iter__(self):
        """迭代链表中的时间段节点。"""
        node = self.head.load
        while node != self.tail:
            yield node
            node = node.next

    def append(self, new_node):
        """
        在链表末尾追加新节点。

        :param new_node: 要追加的新节点。
        """
        current_last = self.tail.front
        current_last.next = new_node
        new_node.front = current_last
        new_node.next = self.tail
        self.tail.front = new_node

    def __getitem__(self, index):
        """
        获取链表中指定索引的节点。

        :param index: 索引值（支持切片）。
        :return: 节点或节点列表。
        :raises IndexError: 如果索引超出范围。
        :raises TypeError: 如果索引类型无效。
        """
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            result = []
            current = self.head.load
            count = 0
            while current != self.tail:
                if start <= count < stop:
                    if (count - start) % step == 0:
                        result.append(current)
                count += 1
                current = current.next
            return result
        elif isinstance(index, int):
            if index < 0:
                index = len(self) + index  # 支持负索引
            if index < 0 or index >= len(self):
                raise IndexError("Index out of range")
            current = self.head.load
            count = 0
            while current != self.tail:
                if count == index:
                    return current
                current = current.next
                count += 1
        else:
            raise TypeError("Invalid index type")

    def __len__(self):
        """返回链表的长度。"""
        return sum(1 for _ in self)


class TimeList:
    """
    管理有序时间段集合。
    """

    def __init__(self, initial_times: list[Time], order: str = 'start'):
        """
        初始化时间段集合。

        :param initial_times: 初始时间段列表。
        :param order: 排序依据（'start' 或 'end'）。
        :raises ValueError: 如果初始时间段列表为空。
        """
        if not initial_times:
            raise ValueError("Initial times cannot be empty")

        self.order = order
        initial_times.sort(key=lambda t: getattr(t, order))
        self.time_list = initial_times

    def find_insert_index(self, new_time: Time) -> int:
        """
        使用二分查找找到新时间段的插入位置。

        :param new_time: 要插入的新时间段。
        :return: 插入位置的索引。
        """
        left, right = 0, len(self.time_list)
        while left < right:
            mid = (left + right) // 2
            if getattr(self.time_list[mid], self.order) < getattr(new_time, self.order):
                left = mid + 1
            else:
                right = mid
        return left

    def split(self, split_time):
        """
        在指定时间点分割时间段。
        返回分割后的前面的时间段索引。
        :param split_time: 分割时间点（1个）
        """
        for i, time in enumerate(self.time_list):
            if time.start < split_time < time.end:
                front_part, back_part = time.split(split_time)
                self.time_list[i] = front_part
                self.time_list.insert(i + 1, back_part)
                return i
            elif split_time == time.start:
                return i-1
            elif split_time == time.end:
                return i

    def append(self, time: Time):
        """
        追加时间段到集合中。

        :param time: 要追加的时间段。
        :raises TypeError: 如果输入不是 Time 类型。
        :raises ValueError: 如果时间段与现有时间段冲突。
        """
        if not isinstance(time, Time):
            raise TypeError("time must be a Time")
        if any(time.is_conflict() for time in self.time_list):
            raise ValueError("Time conflict detected")
        index = self.find_insert_index(time)
        self.time_list.insert(index, time)

    def extend(self, time_list: 'TimeList'):
        """
        扩展时间段集合。

        :param time_list: 要扩展的时间段集合。
        :raises TypeError: 如果输入不是 TimeList 类型。
        """
        if not isinstance(time_list, TimeList):
            raise TypeError("time_list must be a TimeList")
        for time in time_list:
            self.append(time)

    def __add__(self, other):
        """
        合并时间段集合或单个时间段。

        :param other: 要合并的时间段或时间段集合。
        :return: 合并后的 TimeList 实例。
        :raises TypeError: 如果输入类型无效。
        """
        if isinstance(other, Time):
            self.append(other)
        elif isinstance(other, TimeList):
            self.extend(other)
        else:
            raise TypeError("other must be a Time or TimeList")
        return self

    def pop(self, time: Time):
        """
        从集合中移除时间段。

        :param time: 要移除的时间段。
        """
        self.time_list.remove(time)

    def delete(self, time: Time):
        """
        从集合和链表中移除时间段。

        :param time: 要移除的时间段。
        """
        self.pop(time)
        time.remove()
    def replace(self, new_time: Time,old_time: Time = None, index:int = None):
        """
        替换集合中的时间段。
        :param index:
        :param old_time: 要替换的旧时间段。
        :param new_time: 要替换的新时间段。
        :raises ValueError: 如果新时间段与现有时间段冲突。
        """
        if not index:
            index = self.time_list.index(old_time)
        self.time_list[index] = new_time
        old_time.replace(new_time)

    def __sub__(self, other: 'TimeList'):
        """
        减去另一个时间段集合。

        :param other: 要减去的时间段集合。
        :return: 减去后的 TimeList 实例。
        :raises TypeError: 如果输入不是 TimeList 类型。
        """
        if not isinstance(other, TimeList):
            raise TypeError("other must be a TimeList")
        for time in other:
            if time in self.time_list:
                self.pop(time)
        return self

    def is_in(self, time: Time) -> bool:
        """
        检查时间段是否在集合中。

        :param time: 要检查的时间段。
        :return: 如果存在返回 True，否则返回 False。
        """
        return time in self.time_list

    def find(self, time_point: float) -> Time:
        """
        查找包含指定时间点的时间段。

        :param time_point: 要查找的时间点。
        :return: 包含该时间点的时间段。
        :raises ValueError: 如果找不到对应的时间段。
        """
        for time in self.time_list:
            if time.start <= time_point <= time.end:
                return time
        raise ValueError(f"No time segment contains the time point {time_point}")

    def __contains__(self, item):
        """检查时间段是否在集合中。"""
        return item in self.time_list

    def __iter__(self):
        """迭代时间段集合。"""
        return iter(self.time_list)

    def __getitem__(self, item):
        """获取指定索引的时间段。"""
        return self.time_list[item]

    def __len__(self):
        """返回时间段集合的长度。"""
        return len(self.time_list)