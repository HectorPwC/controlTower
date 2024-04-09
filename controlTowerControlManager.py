import sys
import json
import datetime
import logging
import boto3
import concurrent.futures
import threading
#Uncomment time import if you are using sleep
#import time

controlsToRemove = list()
userAction = ''
aws_codes = ''

def main():
    """
    Method main:
    Checks if at least one parameter is there.
    """
    if len(sys.argv) < 2:
        print("No arguments provided")
        print("Usage: python controlTowerControlManager.py enable/disable")
        sys.exit(1)
    else:
        return sys.argv[1]

def executeControlTowerCommand(control):
    """
    Runs an Enable or Disable command against Control Tower.
    """
    starttime = datetime.datetime.now()
    controlsToRemove.append(control)
    logging.info(f"Thread '{control}' starting")
    response = None
    try:
        control_arn = loadCommands(control, region)
        client = boto3.client('controltower')
        if userAction == 'enable':
            response = client.enable_control(
                controlIdentifier= control_arn,
                targetIdentifier=f"arn:aws:organizations::{organization}:ou/{ou}",
                tags={'CreatedControl': 'ScriptCreated'},
            )
        elif userAction == 'disable':
            response = client.disable_control(
                controlIdentifier= control_arn,
                targetIdentifier=f"arn:aws:organizations::{organization}:ou/{ou}"
            )
        elif userAction == 'list':
            response = client.list_enabled_controls( maxResults=500, nextToken='nextList', targetIdentifier=f"arn:aws:organizations::{organization}:ou/{ou}")
        else:
            print('Invalid parameter. Please use "enable", "disable", "list"')
            sys.exit(1)
        endtime = datetime.datetime.now()
        return f"Thread response {response}', start: {starttime}, ended: {endtime}"
    except Exception as err:
        print(f"Command: {control} Error: {err=}")
        return ""


def loadCommands(command_name, region_name):
    """
    Loads the correct command for a region based on the command name.
    Commands that have periods in the name have a hash that represents the command call.
    This uses the values in the aws_codes.json file.
    """
    cmd = list(filter(lambda command: command["commandName"] == command_name, aws_codes))
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
        
def taskDone(future):
    """
    Method that is called after a thread is completed.
    We can use it to document times, or do any kind of thread cleanup we need to do.
    """
    try:
        print(f"This tast is done: {threading.current_thread().name}, future result: {future.result()}")
    except Exception as err:
        print(f"Task Done Error: {err=}")

if __name__ == "__main__":
    userAction = main()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info("Process Stating")

    #Read the configuration file and load it into a local variable
    configContent = ''
    with open("config.json", "r") as f:
        configContent= json.load(f)

    #Load all of the AWS commands per name by region.
    with open('aws_codes.json', 'r') as file:
        aws_codes = json.load(file)

    #Populate the local variables based on the configuration
    region = configContent['region']
    thread_count = configContent['thread_count']
    organization = configContent['organization']
    ou = configContent['ou']
    controls = configContent['controls']

    futures = list()
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            for control in controls[:thread_count]:
                future = executor.submit(executeControlTowerCommand, control)
                future.add_done_callback(taskDone)
                futures.append(future)

        #Use this sleep to pause between batches of commands. Include a Sleep Timer property in the configuration and use it here.
        #time.sleep(SleepTimerFromConfig)
                
        #Remove controls from the loaded configuration after threads have been executed so we do not dupplicate the execution.
        for control in controlsToRemove:
            controls.remove(control)
        controlsToRemove.clear()
        if len(controls) == 0:
            break

    logging.info("All Items done")