import sys
import os
import asyncio

sys.path.append(os.getcwd())

from distributors.search_tasks.consumer import search_tasks_consumer


if __name__ == '__main__':
    asyncio.run(search_tasks_consumer())
