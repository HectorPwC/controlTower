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
# https://docs.aws.amazon.com/controltower/latest/userguide/control-api-examples-short.html

def addThreadToList(control):
    starttime = datetime.datetime.now()
    controlsToRemove.append(control)
    logging.info(f"Thread '{control}' starting")
    try:
        control_arn = loadCommands(control, region)
        client = boto3.client('controltower')
        response = client.enable_control(
            controlIdentifier= control_arn,
            targetIdentifier=f"arn:aws:organizations::{organization}:ou/{ou}",
            tags={'CreatedControl': 'ScriptCreated'},
         )

        #time.sleep(random.randrange(10))
        endtime = datetime.datetime.now()
        return f"Thread response {response}', start: {starttime}, ended: {endtime}"
    except Exception as err:
        print(f"Command: {control} Error: {err=}")
        return ""
    # logging.info(f"Thread '{cli_command}' finishing")

def taskDone(future):
    try:
        print(f"This tast is done: {threading.current_thread().name}, future result: {future.result()}")
    except:
        print("Task Done Error")

def loadCommands(command_name, region_name):
    with open('aws_codes.json', 'r') as file:
        json_content = json.load(file)
        cmd = list(filter(lambda command: command["commandName"] == command_name, json_content))
        if len(cmd) > 0 :
            arn = list(filter(lambda arns: arns["region"] == region_name, cmd[0]["arns"] ))
            if len(arn) > 0:
                return arn[0]["arn"]
            else:
                print("No Arn found")
                return ""
        else:
            print("No Command found")
            return ""

#main
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    # logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    
    f = open("config.json", "r")
    fileContent = json.load(f)
    region = fileContent['region']
    thread_count = fileContent['thread_count']
    organization = fileContent['organization']
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
