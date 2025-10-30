import sys
import os
import asyncio

sys.path.append(os.getcwd())

from distributors.massive_messaging.consumer import massive_messaging_consumer


if __name__ == '__main__':
    asyncio.run(massive_messaging_consumer())
