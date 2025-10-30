import sys
import os
import asyncio

sys.path.append(os.getcwd())

from distributors.freelancer_massages.consumer import new_message_consumer

if __name__ == '__main__':
    asyncio.run(new_message_consumer())