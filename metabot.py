import os
import schedule
from urllib import request
from ast import literal_eval
from time import sleep
from random import choice
from slackclient import SlackClient
from datetime import datetime


# SLACK FUNCTIONS
def handle_command(command, channel, caller):
    if command.startswith(':'):
        command = command[1::]
    response = choice(CONFUSED)
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
            response = "You aren't allowed to do that."
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
            else:
                response = get_help(True, 'get')
        else:
            response = "You aren't allowed to do that."
    elif command.startswith('help'):
        command = command.replace('help', '').replace(' ', '')
        response = get_help(is_admin(name_from_id(caller)[1]), command)
    elif command.startswith('ping'):
        response = 'Pong!'
    elif 'joke' in command:
        response = choice(JOKES)

    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if 'text' in output:
                if 'subtype' in output and 'channel' in output:
                    if (output['type'] == 'channel_join' or output['subtype'] == 'channel_join') and output['channel'] == get_channels(True, 'general')[1]:
                        welcome(output['user'], output['channel'])
                        return None, None, None
                if 'user' in output:
                    print()
                    print(output)
                    if AT_BOT in output['text']:
                        return output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output['user']
                    elif output['channel'][0] == 'D' and output['user'] != BOT_ID:
                        return output['text'].strip().lower(), output['channel'], output['user']

    return None, None, None




# COMMANDS
def welcome(userid, channel):
    userid = userid.upper()
    slack_client.api_call('chat.postMessage', channel=channel, text=choice(GREETINGS).replace('X',name_from_id(userid)[1]), as_user=True)
    slack_client.api_call('chat.postMessage', channel=userid,
                          text="Hi " + name_from_id(userid)[1] + "! \n\nWe've got two rules here: \n\
\n1) Don't be a dick. Respect the admins if they nudge you - They'll be nice, I promise. \
\n2) Try to keep it vaguely on-topic. At least start discussions that are on-topic, \
and if they wander off somewhere interesting then it's not a big deal. \
\n\nIf you have any suggestions or wanna hurl abuse at the admins, your targets are " + ', '.join(get_admins(True)[:-1]) + ' and ' + get_admins(True)[-1] + '. \
\n\nWe suggest that you join some of our channels for extra fun and games: #bitching #game_jams #off-topic #rookie #show-off', as_user=True)
    return ''

def ping():
    slack_client.api_call("chat.postMessage", channel='G1WARM8QM', text="Ping!", as_user=True)

def get_help(admin=False, subcommand=""):
    if admin:
        if subcommand == "":
            return "```Commands:\
\nhelp  -  shows a list of commands (duh!) \
\nping  -  pings the bot host\njoke  -  tells a joke \
\ntest* -  testing bot functions\nget*  -  get slack status values \
\n\n* type 'help command' to view full command```"
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
\nhelp  -  shows a list of commands (duh!) \
\nping  -  pings the bot host\njoke  -  tells a joke```"
        else:
            return "Can't find command: " + subcommand
            
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
                name = i
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
                    response += str(name) + " last updated " + str(daysago) + " days ago\n"
    if getval:
        return isupdate,response
    else:
        if isupdate:
            slack_client.api_call("chat.postMessage", channel='general', text=response, as_user=True)
        return ""





# MAIN
if __name__ == "__main__":
    BOT_ID = os.environ['SLACK_BOT_ID']
    AT_BOT = "<@" + str(BOT_ID) + ">"

    slack_client = SlackClient(os.environ['SLACK_BOT_TOKEN'])
    debug_token = os.environ['SLACK_TEST_TOKEN']

    CONFUSED = [
        "I'm not really sure what you mean", "I'm not sure what you're saying", "I don't understand",
        "What do you mean?", "I'm not sure I understand", "What are you saying?", "Huh?", "¯\_(ツ)_/¯",
        "What are you trying to say?", "What does that mean?", "Could you explain?", "What?"
    ]
    GREETINGS = [
        "Hi X! Welcome to the gamemaker slack!", "Hello X, welcome to the wonderful world of the gamemaker slack!",
        "Oh, hello X!", "Ladies and Gentlemen, it is my great pleasure today to introduce X!",
        "Welcome to the gamemaker slack, X.", "Welcome, X!", "Ooh we have a new person.\nHello X!"
    ]
    JOKES = [
        "Hey, kid. I don't do humour any more...", "What, do you think I'm a clown?", "I don't tell jokes",
        "I'm all outta jokes.", "I'm sorry, but there will be no more jokes. Robots can't do humour.",
        "I'm a robot, not a comedian. Please stop asking me to tell jokes."
    ]

    schedule.every().day.at('19:30').do(check_studio_update)
    ping()
    schedule.every(10).minutes.do(ping)

    READ_WEBSOCKET_DELAY = .5
    if slack_client.rtm_connect():
        print("Bot connected and running! " + str(AT_BOT))
        while True:
            schedule.run_pending()
            command, channel, caller = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, caller)
            sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
