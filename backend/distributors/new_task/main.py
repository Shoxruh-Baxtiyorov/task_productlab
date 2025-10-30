import sys
import os
import asyncio

sys.path.append(os.getcwd())

from distributors.new_task.consumer import new_task_consumer


if __name__ == '__main__':
    asyncio.run(new_task_consumer())
