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
    response = choice(DR['confused'])
    
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
            response = choice(DR['bad_response'])
            
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
            response = choice(DR['bad_response'])
            
    elif command.startswith('help'):
        command = command.replace('help', '').replace(' ', '')
        response = get_help(is_admin(name_from_id(caller)[1]), command)

    elif command.startswith("rules"):
        response = get_rules()
        
    elif command.startswith('ping'):
        response = 'Ping!'
        
    elif command.startswith('feedback'):
        response = "https://goo.gl/forms/hF5IKrx0KQMz3s052"

    elif command.startswith("ghost"): # THIS FUNCTION SHOULD ONLY WORK FOR RILIN
        if name_from_id(caller)[1] in get_admins(True):
            command = command.replace('ghost ', '')
            channel = command[:9]
            response = command[10:]

    sc.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if 'text' in output:
                if 'subtype' in output and 'channel' in output:
                    if (output['type'] == 'channel_join' or output['subtype'] == 'channel_join') and output['channel'] == get_channels(True, 'lounge')[1]:
                        welcome(output['user'], output['channel'])
                        return None, None, None
                elif 'pug' in output['text'] and output['user'] != BOT_ID:
                    if (randint(0,2) == 0) or output['text'] == '`grumpypug`':
                        sc.api_call("chat.postMessage", channel=output['channel'], text=':grumpypug0::grumpypug1::grumpypug2:', as_user=True)
                    return None, None, None
                elif 'ghost' in output['text'] and output['user'] == 'U1NQUSSEQ':
                    return output['text'], output['channel'], output['user']
                elif output['channel'][0] == 'D' and output['user'] != BOT_ID:
                    return output['text'].strip().lower(), output['channel'], output['user']
                elif 'user' in output:
                    if output['text'].startswith(AT_BOT):
                        return output['text'].split(AT_BOT)[1].lower().strip(), output['channel'], output['user']
                    elif output['text'].lower().startswith('meta'):
                        return output['text'].lower().split('meta')[1].strip(), output['channel'], output['user']
                    elif output['text'].startswith('!m'):
                        return output['text'].split('!m')[1].lower().strip(), output['channel'], output['user']

    return None, None, None


# COMMANDS
def welcome(userid, channel):
    userid = userid.upper()
    sc.api_call('chat.postMessage', channel=channel, text=choice(DR['greetings']).replace('<N>',name_from_id(userid)[1]), as_user=True)
    sc.api_call('chat.postMessage', channel=userid,
                          text=DR['intro'][0].replace('<N>', name_from_id(userid)[1]).replace('<A>', '@'+', @'.join(get_admins(True)[:-1])+' &amp; @'+get_admins(True)[-1]), as_user=True)
    return ''


def get_help(admin=False, subcommand=""):
    if admin:
        if subcommand == "":
            return "```Commands:\
\nget*   -  get slack status values\
\nhelp   -  shows a list of commands (duh!)\
\nping   -  pings the bot host\
\ntest*  -  testing bot functions\
\nrules  -  shows a list of the rules\
\nfeedback - get link to feedback form\
\n\n* type 'help [command]' to view full command```"
        else:
            if subcommand == "get":
                return "```Fetches data from the slack client\nUsage: get [admins|users|name|channel|id] (value)```"
            elif subcommand == "test":
                return "```Tests bot system commands\nUsage: test [welcome|update] (id)```"
            else:
                return "Can't find command: " + subcommand
    else:
        if subcommand == "":
            return "```Commands:\
\nhelp  -  shows a list of commands (duh!)\
\nping  -  pings the bot host\
\nrules -  shows a list of the rules\
\nfeedback - get link to feedback form```"
        else:
            return "Can't find command: " + subcommand


def get_rules():
    return DR['rules'][0].replace('<A>', '@'+', @'.join(get_admins(True)[:-1])+' &amp; @'+get_admins(True)[-1])


def get_channels(only_names=False, channel=""):
    userlist = sc.api_call('channels.list', token=debug_token)
    if channel == "":
        if only_names == True:
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
    userlist = sc.api_call('users.list', token=debug_token)
    if justnames == True:
        namelist = []
        for i in userlist['members']:
            namelist += [i['name']]
        return namelist
    else:
        return userlist


def get_user_ids():
    userlist = sc.api_call('users.list', token=debug_token)
    idlist = []
    for i in userlist['members']:
        idlist += [i['id']]
    return idlist


def get_admins(justnames=False):
    userlist = sc.api_call('users.list', token=debug_token)
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
    # The update checker for gamemaker studio has been removed since it is not being updated regularly anymore
    # This now checks for updates to gamemaker studio 2
    RSS = request.urlopen('http://gms.yoyogames.com/update-win.rss')
    #print(RSS.read())
    return ""



# MAIN
if __name__ == "__main__":
    BOT_ID = os.environ['SLACK_BOT_ID']
    AT_BOT = "<@" + str(BOT_ID) + ">"
    HOSTED = int(os.getenv('SLACK_HOSTED', 0))
    END = False

    sc = SlackClient(os.environ['SLACK_BOT_TOKEN'])
    debug_token = os.environ['SLACK_TEST_TOKEN']

    with open('data/defaultresponses.json') as data_file:
        DR = json.load(data_file)

    with open('data/selfintro.json') as data_file:
        SELF_INTRO = json.load(data_file)

    READ_WEBSOCKET_DELAY = .5
    if sc.rtm_connect():
        print("Bot connected and running! " + str(AT_BOT))

        # This code only runs when the bot is on the server
        if HOSTED:
            # Hello world start
            sc.api_call("chat.postMessage", channel=id_from_name('rilin')[1], text="Starting..", as_user=True)
            # Random chance for bot to say something in #lounge
            if randint(0,40) == 1:
                depressed_text = choice(DR['depressed'])
                if "Hehehe" in depressed_text:
                    sc.api_call('chat.postMessage', channel=get_channels(True, 'lounge')[1], text="", attachments=SELF_INTRO, as_user=True)
                else:
                    sc.api_call('chat.postMessage', channel=get_channels(True, 'lounge')[1], text=depressed_text, as_user=True)
                sc.api_call("chat.postMessage", channel=id_from_name('rilin')[1], text="I'm not feeling too well...", as_user=True)
            # Bot checks for and announces updates to gamemaker studio
            check_studio_update()

        # Main loop; bot checks for message, responds, sleeps, repeats
        check_studio_update()
        while END == False:
            command, channel, caller = parse_slack_output(sc.rtm_read())
            if command and channel:
                handle_command(command, channel, caller)
            sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
