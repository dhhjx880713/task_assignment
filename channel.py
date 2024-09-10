
import logging
from utils.log_utils import get_logger
from typing import Union
from task import AllocatedTask


class OccupiedInfo:

    def __init__(self, occupied_period, task_id, occupied_bandwidth) -> None:
        self.occupied_period = occupied_period
        self.task_id = task_id
        self.occupied_bandwidth = occupied_bandwidth

    def __repr__(self) -> str:
        return f"Task ID: {self.task_id}, \
                occupied period: {self.occupied_period}, \
                occupied bandwidth: {self.occupied_bandwidth}"


class Channel:

    def __init__(self, id: int, bandwidth: int, 
                 allocated_tasks: list, t_max: int = 90,
                 price: int = 0, 
                 logger: Union[None, str, logging.Logger] = None) -> None:
        self.id = id
        self.bandwidth = bandwidth
        self.allocated_tasks = allocated_tasks
        self.t_max = t_max
        self.price = price
        self.logger = get_logger(logger)
    
    def __repr__(self) -> str:
        return f"Channel ID: {self.id}, channel bandwidth: {self.bandwidth}"
    
    def allocate_task(self, task):
        if task.bandwidth > self.bandwidth or task.end_time > self.t_max:
            self.logger.error(f"Cannot allocate task {task.id}")
            return False
        else:
            # loop all the available frequency to find the available solution 
            # with minimum fragmentation
            frag_levels = []
            start_freq_candidates = []
            for b in range(self.bandwidth - task.bandwidth):
                # check if there is occuption in the given time
                if not self.is_occupied(b, b + task.bandwidth, 
                                        task.start_time, task.end_time):
                    # create a new allocated task
                    new_allocated_task = AllocatedTask(
                        task.id,
                        available_channels=[self.id],
                        start_freq=b, 
                        end_freq=b+task.bandwidth,
                        start_time=task.start_time,
                        end_time=task.end_time,
                        priority=task.priority,
                        bid=task.bid)
                    self.allocated_tasks.append(new_allocated_task)
                    task.is_assigned = True
                    # compute fragmentation level
                    frag_levels.append(self.compute_fragmentation())
                    # remove the pre-assigned task
                    # self.allocated_tasks = self.allocated_tasks.pop()
                    self.allocated_tasks = self.allocated_tasks[:-1]
                    task.is_assigned = False
                    start_freq_candidates.append(b)
            if start_freq_candidates == []:
                self.logger.info(f"Task {task.id} cannot be allocated in channel {self.id}.")
                return False
            else:
                min_idx = min(range(len(frag_levels)), 
                              key=frag_levels.__getitem__)
                start_freq = start_freq_candidates[min_idx]
                new_allocated_task = AllocatedTask(
                    task.id,
                    available_channels=[self.id],
                    start_freq=start_freq,
                    end_freq=start_freq + task.bandwidth,
                    start_time=task.start_time,
                    end_time=task.end_time,
                    priority=task.priority,
                    bid=task.bid)
                self.allocated_tasks.append(new_allocated_task)
                task.is_assigned = True
                self.logger.info(f"Task {task.id} is allocated in channel {self.id} \
                                 start time: {new_allocated_task.start_time}, \
                                 end time: {new_allocated_task.end_time}, \
                                 start frequency: {new_allocated_task.start_freq}, \
                                 end_frequency: {new_allocated_task.end_freq}")
                return True

    def is_occupied(self, start_freq, end_freq, start_time, end_time):
        target_area = (start_time, start_freq, end_time, end_freq)

        for allocated_task in self.allocated_tasks:
            task_area = allocated_task.get_bounding_box()
            if do_rectangles_intersect(target_area, task_area):
                return True
        return False
    
    def calculate_priority_gain(self, task):
        if not task.is_assigned:
            if self.allocate_task(task):
                priority_gain = 1.0 / task.priority
                return priority_gain
            else:
                return 0
        else:
            return 0  # should not return the same value as 0 gain
    
    def compute_fragmentation(self):
        """compute the area of a bounding box which can contain all
           the tasks in the channel
        """
        x_values = []
        y_values = []
        if self.allocated_tasks != []:
            for allocated_task in self.allocated_tasks:
                x1, y1, x2, y2 = allocated_task.get_bounding_box()
                x_values.append(x1)
                x_values.append(x2)
                y_values.append(y1)
                y_values.append(y2)
            x_min = min(x_values)
            x_max = max(x_values)
            y_min = min(y_values)
            y_max = max(y_values)
            area = (x_max - x_min) * (y_max - y_min)
            return area
        else:
            return 0
        
    def get_channel_capacity(self):
        return self.t_max * self.bandwidth
    
    def get_occupied_resource(self):
        if self.allocated_tasks != []:
            occupied_resource = 0
            for allocated_task in self.allocated_tasks:
                occupied_resource += allocated_task.get_required_resource()
            return occupied_resource
        else:
            return 0
    
    def get_occupation_rate(self):
        occupied_resource = self.get_occupied_resource()
        channel_capacity = self.get_channel_capacity()
        return occupied_resource / channel_capacity


def check_tasks_overlap(allocated_task1, allocated_task2):
    # check if two allocated tasks overlap each othter or not
    # Basically, the idea is to check if two rectangles intersect
    # with each other or not
    box_a = (allocated_task1.start_time, allocated_task1.start_freq,
             allocated_task1.end_time, allocated_task1.end_freq)
    box_b = (allocated_task2.start_time, allocated_task2.start_freq,
             allocated_task2.end_time, allocated_task2.end_freq)
    return do_rectangles_intersect(box_a, box_b)


def do_rectangles_intersect(A, B):
    # A is (A_x1, A_y1, A_x2, A_y2)
    # B is (B_x1, B_y1, B_x2, B_y2)

    # Check if one rectangle is completely to the left, right, above, or below the other
    if A[2] <= B[0] or B[2] <= A[0]:  # One is to the left of the other
        return False
    if A[3] <= B[1] or B[3] <= A[1]:  # One is below the other
        return False

    # Otherwise, they intersect
    return True
