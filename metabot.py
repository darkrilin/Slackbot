import os
import pickle
from pprint import pprint
from time import sleep
from random import choice
from slackclient import SlackClient


# SLACK FUNCTIONS
def handle_command(command, channel):
    if command.startswith(':'):
        command = command[1::]
    response = choice(CONFUSED)
    if command.startswith('get_admins'):
        response = ', '.join(get_admins(True))
        #get_users(True))
    elif command.startswith('is_admin'):
        command = command.replace('is_admin ','')
        response = is_admin(command)[1]
    elif command.startswith('get_users'):
        response = ', '.join(get_users(True))
    elif command.startswith('get_name'):
        command = command.replace('get_name ', '')
        response = name_from_id(command)[1]
    elif command.startswith('get_id'):
        command = command.replace('get_id ', '')
        response = id_from_name(command)[1]
    else:
        text = command.replace('\n', ' ').replace('\r', '').lower()
        for p in PUNCTUATION:
            text = text.replace(p, '')
        text = text.split(' ')
        text.sort()
        print(text)
        response = choice(CONFUSED)
        
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        if output_list[0]['type'] == 'message':
            print(output_list)
            print('')
        for output in output_list:
            if 'text' in output:
                if AT_BOT in output['text']:
                    return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
                elif output['channel'][0] == 'D' and output['user'] != BOT_ID:
                    return output['text'].strip().lower(), output['channel']
    return None, None


# COMMANDS
def get_users(justnames=False):
    userlist = slack_client.api_call('users.list', token=debug_token)
    if justnames == True:
        namelist = []
        for i in userlist['members']:
            namelist += [i['name']]
        return namelist
    else:
        return userlist

def get_user_ids():
    userlist = slack_client.api_call('users.list', token=debug_token)
    idlist = []
    for i in userlist['members']:
        idlist += [i['id']]
    return idlist

def get_admins(justnames=False):
    userlist = slack_client.api_call('users.list', token=debug_token)
    namelist = []
    for i in userlist['members']:
        if 'is_admin' in i.keys():
            if i['is_admin'] == True:
                namelist += [i['name']]
    return namelist

def is_admin(name):
    if name in get_users(True):
        if name in get_admins(True):
            return True,"Of course " + name + " is an admin... Didn't ya know?"
        return False,"Of course not!"
    elif name.upper() in get_user_ids():
        if name_from_id(name.upper())[1] in get_admins(True):
            return True,"Of course " + name_from_id(name.upper())[1] + " is an admin... Didn't ya know?"
        return False,"Of course not!"
    else:
        return False,'*"WHO IS THIS ' + name.upper() + ' YOU SPEAK OF"*'

def name_from_id(userid):
    userlist = get_users()
    for i in userlist['members']:
        if i['id'] == userid.upper():
            return True,i['name']
    return False,"Incorrect ID"

def id_from_name(username):
    userlist = get_users()
    for i in userlist['members']:
        if i['name'] == username:
            return True,i['id']
    return False,'*"WHO IS THIS ' + username.upper() + ' YOU SPEAK OF"*'


# MAIN
if __name__ == "__main__":
    BOT_ID = os.environ.get('SLACK_BOT_ID')#, 'U1WBVJF8A')
    AT_BOT = "<@" + str(BOT_ID) + ">"

    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    debug_token = os.environ.get('SLACK_TEST_TOKEN')

    CONFUSED = [
        "I'm not really sure what you mean", "I'm not sure what you're saying", "I don't understand",
        "What do you mean?", "I'm not sure I understand", "What are you saying?", "Huh?", "¯\_(ツ)_/¯",
        "What are you trying to say?", "What does that mean?", "Could you explain?", "What?"
    ]
    PUNCTUATION = ['.',',','?','!',"'",';']
    
    READ_WEBSOCKET_DELAY = .5
    
    if slack_client.rtm_connect():
        print("Bot connected and running! " + str(AT_BOT))
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
