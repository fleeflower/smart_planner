from data_structure import Task
import numpy as np
from datetime import datetime

class PrioritySorter:
    def __init__(self,buffer: float = 60, k: float = 0.1):
        self.buffer = buffer
        self.k = k

    def get_priority(self, task_list : list[Task]):
        time_anchor = datetime.now()
        task_matrix = self.build_task_matrix(task_list, time_anchor)
        sorted_indices = self.sort_tasks(task_matrix)
        priority_list = [task_list[i] for i in sorted_indices]
        return priority_list

    @staticmethod
    def build_task_matrix(tasks: list[Task]) -> np.ndarray:
        """
        安全构建任务矩阵（带类型校验和异常处理）

        参数:
        tasks : 包含Task对象的可迭代集合

        返回:
        np.ndarray - 形状(N,3)的任务矩阵，包含：
            [数值化紧急度, 持续时间(分钟), 剩余分钟数]
        """
        # 时间基准点校验

        matrix = []
        for idx, task in enumerate(tasks):
            # 类型校验层
            if not isinstance(task.duration, int) or task.duration <= 0:
                raise ValueError(f"任务{idx}的duration需为正整数，获取到{task.duration}")

            if not isinstance(task.deadline, datetime):
                raise TypeError(f"任务{idx}的deadline需为datetime类型，获取到{type(task.deadline)}")

            # 紧急度数值化
            urgency_val = Task.URGENCY_MAP.get(task.urgency.lower(), 1) if task.urgency else 1
            if not isinstance(urgency_val, int):
                raise ValueError(f"任务{idx}紧急度'{task.urgency}'未在映射表中定义")

            remaining_min = task.remaining_time()

            matrix.append([urgency_val, task.duration, remaining_min])

        return np.array(matrix, dtype=np.float64)

    def sort_tasks(self,data: np.ndarray) -> np.ndarray:
        priority = data[:, 0].astype(float)
        duration = data[:, 1].astype(float)
        remaining = data[:, 2].astype(float)

        effective_remaining = remaining - self.buffer

        ratio = np.divide(effective_remaining, duration,
                          where=(duration != 0))  # 避免除零错误

        feasibility = np.where(
            effective_remaining > duration,
            1 + np.log(ratio),  # 时间充裕
            np.where(
                effective_remaining >= 0,
                0.1 * (ratio ** 10),  # 时间紧张
                -1.0  # 已超期
            )
        )

        urgency = 1 / (1 + np.exp(-self.k * (effective_remaining - duration)))

        score = priority * urgency * feasibility

        # 超期任务强制置底（即使高优先级）
        final_score = np.where(effective_remaining < 0, -np.inf, score)

        return np.argsort(-final_score)


