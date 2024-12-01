from channel import Channel
from task import AllocatedTask, Task
from utils.log_utils import get_logger

BANDWIDTH = [36, 54, 72, 300]


def init_tasks():
    task1 = Task(
        id=1,
        available_channels=[1, 2, 3],
        bandwidth=19,
        start_time=45,
        end_time=65,
        priority=1,
        bid=50)

    task2 = Task(
        id=2,
        available_channels=[1, 2, 3],
        bandwidth=24,
        start_time=10,
        end_time=15,
        priority=2,
        bid=20)

    task3 = Task(
        id=3,
        available_channels=[1, 2, 3],
        bandwidth=29,
        start_time=30,
        end_time=76,
        priority=3,
        bid=30)

    task4 = Task(
        id=4,
        available_channels=[1, 2, 3],
        bandwidth=13,
        start_time=20,
        end_time=60,
        priority=4,
        bid=40)

    task5 = Task(
        id=5,
        available_channels=[1, 2, 3],
        bandwidth=33,
        start_time=30,
        end_time=71,
        priority=5,
        bid=40)

    return [task1, task2, task3, task4, task5]


def allocate_resources_greedy(tasks, channels):
    tasks_sorted = sorted(tasks, key=lambda x: x.priority, reverse=True)

    n_tasks = 8
    n_channels = 3
    allocation_matrix = [[0 for _ in range(n_tasks)]
                         for _ in range(n_channels)]
    for task in tasks_sorted:
        print(f'processing task {task.id}')
        for channel in channels:
            if channel.id in task.available_channels:
                if channel.bandwidth >= task.bandwidth:
                    if channel.allocate_task(task):
                        print(f'task {task.id} is allowcated!')
                        allocation_matrix[channel.id - 1][task.id - 1] = 1

    return allocation_matrix


def allocate_tasks(tasks, channels):
    logger = get_logger('Task allocation')
    # sort task by priority
    sorted_tasks = sorted(tasks, key=lambda x: x.priority)
    # sort channel by cost, use channel with lowest cost first
    sorted_channels = sorted(channels, key=lambda x: x.price)
    for task in sorted_tasks:
        logger.debug(f'Current task is {task.id}')
        for channel in sorted_channels:
            logger.debug(f'Current channel is {channel.id}')
            if channel.allocate_task(task):
                break
        if not task.is_assigned:
            logger.info(f'Task {task.id} cannot be assigned!')


def init_channels():
    # init channels
    channel1 = Channel(
        1,
        36, [
            AllocatedTask(
                11, (1), start_time=5, end_time=10, start_freq=0, end_freq=18),
            AllocatedTask(
                12, (1), start_time=1, end_time=3, start_freq=5, end_freq=30)
        ],
        price=10)

    channel2 = Channel(
        2,
        54, [
            AllocatedTask(
                13, (2),
                start_time=10,
                end_time=15,
                start_freq=15,
                end_freq=30),
            AllocatedTask(
                14, (2), start_time=30, end_time=40, start_freq=5, end_freq=10)
        ],
        price=15)

    channel3 = Channel(
        3,
        72, [
            AllocatedTask(
                15, (3),
                start_time=30,
                end_time=45,
                start_freq=10,
                end_freq=24)
        ],
        price=20)

    channels = [channel1, channel2, channel3]
    return channels


def main():

    # init tasks
    tasks = init_tasks()
    # init channels
    channels = init_channels()
    allocate_tasks(tasks, channels)


if __name__ == '__main__':
    main()
