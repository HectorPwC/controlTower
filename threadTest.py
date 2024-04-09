# import logging
# import threading
# import time
# import concurrent.futures

# def thread_function(name):
#     logging.info("Thread %s: starting", name)
#     time.sleep(2)
#     logging.info("Thread %s: finishing", name)

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")

#     with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
#         executor.map(thread_function, range(3))


# # SuperFastPython.com
# # example of waiting for tasks to complete via a pool shutdown
# from time import sleep
# from random import random
# from concurrent.futures import ThreadPoolExecutor
 
# # custom task that will sleep for a variable amount of time
# def task(name):
#     # sleep for less than a second
#     sleep(random())
#     print(f'Done: {name}')
 
# # start the thread pool
# with ThreadPoolExecutor(2) as executor:
#     # submit tasks
#     executor.map(task, range(10))
#     # wait for all tasks to complete
#     print('Waiting for tasks to complete...')
# print('All tasks are done!')


import boto3
import threading
import random
import json
import concurrent.futures
import logging
import time
import datetime

threadingDone = False
threadCount = 0
controlsToRemove = list()

def addThreadToList(control):
    starttime = datetime.datetime.now()
    controlsToRemove.append(control)
    cli_command = f"aws controltower enable-control --control-identifier arn:aws:controltower:{region}::control'/{control} --target-identifier {organization_arn} --output text"
    # logging.info(f"Thread '{cli_command}' starting")

    # client = boto3.client('controltower')
    # response = client.enable_control(
    #     controlIdentifier=f'{control}',
    #     parameters=[
    #         {
    #             'key': 'string',
    #             'value': {...}|[...]|123|123.4|'string'|True|None
    #         },
    #     ],
    #     tags={
    #         'string': 'string'
    #     },
    #     targetIdentifier='string'
    # )

    time.sleep(random.randrange(10))
    endtime = datetime.datetime.now()
    return f"Thread '{control}', start: {starttime}, ended: {endtime}"
    # logging.info(f"Thread '{cli_command}' finishing")

def taskDone(future):
    print(f"This tast is done: {threading.current_thread().name}, future result: {future.result()}")

#main
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    # logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    
    f = open("config.json", "r")
    fileContent = json.load(f)
    region = fileContent['region']
    thread_count = fileContent['thread_count']
    organization_arn = fileContent['organization_arn']
    ou = fileContent['ou']
    controls = fileContent['controls']
    # logging.info(f"R:{region}, Org: {organization_arn}, OU: {ou}, Controls: {controls}")

    futures = list()
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            for control in controls[:thread_count]:
                future = executor.submit(addThreadToList, control)
                future.add_done_callback(taskDone)
                futures.append(future)
            # futures = [executor.submit(addThreadToList, control) for control in controls[:thread_count]]
            # concurrent.futures.wait(futures)

        for control in controlsToRemove:
            controls.remove(control)
        controlsToRemove.clear()
        if len(controls) == 0:
            break

    logging.info("All Items done")