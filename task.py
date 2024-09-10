import logging
from typing import Union
from utils.log_utils import get_logger



class Task:

    def __init__(self, id, available_channels, bandwidth, start_time, 
                 end_time, priority=0, bid=0,
                 logger: Union[None, str, logging.Logger] = None):
        self.id = id
        self.available_channels = available_channels
        self.bandwidth = bandwidth
        self.start_time = start_time
        self.end_time = end_time
        self.priority = priority
        self.bid = bid
        self.is_assigned = False
        self.logger = get_logger(logger)

    def __repr__(self) -> str:
        return f"Task {self.id}: available channels: {self.available_channels}, \
                 bandwidth: {self.bandwidth}, start time: {self.start_time}, \
                 end time: {self.end_time}, priority: {self.priority}, \
                 bid: {self.bid}"
    
    def get_required_resource(self):
        return self.bandwidth * (self.end_time - self.start_time)
    
    def check_state(self):
        if self.is_assigned:
            self.logger.info("The task has been assigned!")
        else:
            self.logger.info("The task has not been assigned!")    

class AllocatedTask(Task):

    def __init__(self, id, available_channels, start_freq, end_freq,
                 start_time, end_time, priority=0, bid=0):
        super().__init__(id, available_channels, end_freq - start_freq, 
                         start_time, end_time, priority, bid)
        self.start_freq = start_freq
        self.end_freq = end_freq

    def __repr__(self) -> str:
        return super().__repr__() + f"start bandwidth: {self.start_freq} \
                                      end bandwidth: {self.end_freq}"
    
    def get_bounding_box(self) -> tuple:
        return (self.start_time, self.start_freq, 
                self.end_time, self.end_freq)