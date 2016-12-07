import os
import json
from urllib import request
from ast import literal_eval
from time import sleep
from random import choice, randint
from slackclient import SlackClient
from datetime import datetime


# SLACK FUNCTIONS
def handle_command(command, channel, caller):
    if command.startswith(':'):
        command = command[1::]
        
    response = choice(DEFAULT_RESPONSES['confused'])
    if command.startswith('test'):
        if name_from_id(caller)[1] in get_admins(True):
            command = command.replace('test ', '')
            if command.startswith('welcome'):
                command = command.replace('welcome ', '')
                response = welcome(command, channel)
            elif 'update' in command:
                response = check_studio_update(True)[1]
            else:
                response = get_help(True, 'test')
        else:
            response = choice(DEFAULT_RESPONSES['badresponse'])
            
    elif command.startswith('get'):
        if name_from_id(caller)[1] in get_admins(True):
            if 'admin' in command:
                response = get_admins(True)
            elif 'user' in command:
                response = get_users(True)
            elif 'name' in command:
                command = command.split(' ')[-1]
                response = name_from_id(command)[1]
            elif 'channel' in command:
                command = command.replace('get ','').replace('channel','').split(' ')
                if len(command) == 1:
                    response = [i[0] for i in get_channels(True)]
                else:
                    response = get_channels(True, command[-1])
            elif 'id' in command:
                command = command.split(' ')[-1]
                response = id_from_name(command)[1]
            elif 'time' in command:
                response = get_time()
            else:
                response = get_help(True, 'get')
        else:
            response = choice(DEFAULT_RESPONSES['badresponse'])
            
    elif command.startswith('help'):
        command = command.replace('help', '').replace(' ', '')
        response = get_help(is_admin(name_from_id(caller)[1]), command)
        
    elif command.startswith("rules"):
        response = get_rules()
        
    elif command.startswith('ping'):
        response = 'Pong!'
        
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if 'text' in output:
                if 'subtype' in output and 'channel' in output:
                    if (output['type'] == 'channel_join' or output['subtype'] == 'channel_join') and output['channel'] == get_channels(True, 'lounge')[1]:
                        welcome(output['user'], output['channel'])
                        return None, None, None
                if 'user' in output:
                    if AT_BOT in output['text']:
                        return output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output['user']
                    elif output['text'][-1] == '?':
                        if randint(0,6) == 1:
                            slack_client.api_call("chat.postMessage", channel=output['channel'], text=choice(DEFAULT_RESPONSES['qmark']).replace('__shrug__','¯\_(ツ)_/¯'), as_user=True)
                    elif output['channel'][0] == 'D' and output['user'] != BOT_ID:
                        return output['text'].strip().lower(), output['channel'], output['user']
    return None, None, None


# COMMANDS
def welcome(userid, channel):
    userid = userid.upper()
    slack_client.api_call('chat.postMessage', channel=channel, text=choice(DEFAULT_RESPONSES['greetings']).replace('X',name_from_id(userid)[1]), as_user=True)
    slack_client.api_call('chat.postMessage', channel=userid,
                          text=DEFAULT_RESPONSES['intro'].replace('<NAME>', name_from_id(userid)[1]).replace('<ADMINS>', '@'+', @'.join(get_admins(True)[:-1])+' &amp; @'+get_admins(True)[-1]), as_user=True)
    return ''


def ping():
    slack_client.api_call("chat.postMessage", channel='G1WARM8QM', text="Ping!", as_user=True)


def get_help(admin=False, subcommand=""):
    if admin:
        if subcommand == "":
            return "```Commands:\
\nget*   -  get slack status values\nhelp   -  shows a list of commands (duh!)\
\nping   -  pings the bot host\ntest*  -  testing bot functions\
\nrules  -  shows a list of the rules\
\n\n* type 'help [command]' to view full command```"
        else:
            if subcommand == "get":
                return "```Fetches data from the slack client\nUsage: get [admins|users|name|channel|id] (value)```"
            elif subcommand == "test":
                return "```Tests bot system commands\nUsage: test [welcome|update]```"
            else:
                return "Can't find command: " + subcommand
    else:
        if subcommand == "":
            return "```Commands:\
\nhelp  -  shows a list of commands (duh!)\
\nping  -  pings the bot host\
\nrules -  shows a list of the rules```"
        else:
            return "Can't find command: " + subcommand


def get_rules():
    return DEFAULT_RESPONSES['rules'].replace('<ADMINS>', '@'+', @'.join(get_admins(True)[:-1])+' &amp; @'+get_admins(True)[-1])


def get_channels(justnames=False, channel=""):
    userlist = slack_client.api_call('channels.list', token=debug_token)
    if channel == "":
        if justnames == True:
            namelist = []
            for i in userlist['channels']:
                if i['is_archived'] == False:
                    namelist += [(i['name'], i['id'])]
            return namelist
        else:
            return userlist
    else:
        for i in get_channels(True):
            if channel == i[0] or channel.upper() == i[1]:
                return i[0], i[1]
        return False


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


def get_time():
    return datetime.now().replace(microsecond=0)


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


def check_studio_update(getval=False):
    urls = ['http://gmapi.gnysek.pl/version/gmstudio','http://gmapi.gnysek.pl/version/gmstudiobeta','http://gmapi.gnysek.pl/version/gmstudioea']
    isupdate = False
    response = "*No updates available*\n"
    for i in urls:
        source = literal_eval(str(request.urlopen(i).read())[2:-1])
        if isupdate == False:
            for i in source:
                name = str(i)
                daysago = source[name]['daysAgo']
                if daysago == '0':
                    isupdate = True
                    if name == 'gmstudio':
                        response = "GameMaker:Studio updated to v" + source[name]['version'] + "! http://store.yoyogames.com/downloads/gm-studio/release-notes-studio.html"
                    elif name == 'gmstudiobeta':
                        response = "GameMaker:Studio *Beta* updated to v" + source[name]['version'] + "! http://store.yoyogames.com/downloads/gm-studio/release-notes-studio.html"
                    elif name == 'gmstudioea':
                        response = "GameMaker:Studio Early Access updated to v" + source[name]['version'] + "! http://store.yoyogames.com/downloads/gm-studio-ea/release-notes-studio.html"
                else:
                    response += name.replace('gmstudiobeta','GameMaker:Studio *Beta*').replace('gmstudioea','GameMaker:Studio *_Early Access_*').replace('gmstudio','GameMaker:Studio') + " last updated to v" + source[name]['version'] + ", " + str(daysago) + " days ago\n"
    if getval:
        return isupdate,response
    else:
        if isupdate:
            slack_client.api_call("chat.postMessage", channel=get_channels(True, 'lounge')[1], text=response, as_user=True)
        return ""


# MAIN
if __name__ == "__main__":
    BOT_ID = os.environ['SLACK_BOT_ID']
    AT_BOT = "<@" + str(BOT_ID) + ">"
    HOSTED = int(os.getenv('SLACK_HOSTED', 0))

    slack_client = SlackClient(os.environ['SLACK_BOT_TOKEN'])
    debug_token = os.environ['SLACK_TEST_TOKEN']

    with open('data/defaultresponses.json') as data_file:
        DEFAULT_RESPONSES = json.load(data_file)

    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print("Bot connected and running! " + str(AT_BOT))
        if HOSTED == 1:
            slack_client.api_call("chat.postMessage", channel=id_from_name('rilin')[1], text="Bot starting.", as_user=True)
            if randint(0,24) == 1:
                slack_client.api_call('chat.postMessage', channel=get_channels(True, 'lounge')[1], text=choice(DEFAULT_RESPONSES['depressed']), as_user=True)
                slack_client.api_call("chat.postMessage", channel=id_from_name('rilin')[1], text="I'm not feeling too well...", as_user=True)
            check_studio_update()
        while True:
            command, channel, caller = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, caller)
            sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
