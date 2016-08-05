import os
from time import sleep
from random import choice
from slackclient import SlackClient


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
            else:
                response = get_help(True, 'test')
        else:
            response = "You aren't allowed to do that."
    elif command.startswith('get'):
        if name_from_id(caller)[1] in get_admins(True):
            if 'admin' in command:
                response = ', '.join(get_admins(True))
            elif 'user' in command:
                response = ', '.join(get_users(True))
            elif 'name' in command:
                command = command.split(' ')[-1]
                response = name_from_id(command)[1]
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
                    if (output['type'] == 'channel_join' or output['subtype'] == 'channel_join') and output['channel'] == 'C07EK648H':
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
                return "```Fetches data from the slack client\nUsage: get [admins|users|name|id] (value)```"
            elif subcommand == "test":
                return "```Tests bot system commands\nUsage: test [welcome]```"
            else:
                return "Can't find command: " + subcommand
    else:
        if subcommand == "":
            return "```Commands:\
\nhelp  -  shows a list of commands (duh!) \
\nping  -  pings the bot host\njoke  -  tells a joke```"
        else:
            return "Can't find command: " + subcommand
            

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
        "Welcome to the motherland, comrade!", "Oh, hello X!", "Ladies and Gentlemen, it is my great pleasure today to introduce X!",
        "Welcome to the gamemaker slack, X.", "Welcome, X!", "Ooh we have a new person.\nHello X!"
    ]
    JOKES = [
	"There are only 10 types of people in the world: those that understand binary and those that don’t.",
	"Failure is not an option. It comes bundled with your Microsoft product.",
	"I’m not anti-social; I’m just not user friendly.",
	"My attitude isn’t bad. It’s in beta.",
	"Latest survey shows that 3 out of 4 people make up 75% of the world’s population.",
	"What do you get when you cross a cow and a trampoline? A milkshake.",
	"Mother, “How was school today, Patrick?”\n\nPatrick, “It was really great mum! Today we made explosives!”\n\nMother, “Ooh, they do very fancy stuff with you these days. And what will you do at school tomorrow?”\n\nPatrick, “What school?”",
	'Police officer: "Can you identify yourself, sir?"\n\nDriver pulls out his mirror and says: "Yes, '+"it's me."+'"',
	"I can’t believe I forgot to go to the gym today. That’s 7 years in a row now.",
	"A naked woman robbed a bank. Nobody could remember her face.",
	"The 21st century: Deleting history is often more important than making it.",
	"Woke up with a dead leg this morning. I will not take out a loan with the mafia ever again.",
	"Why do cows wear bells?\n\nTheir horns don’t work.",
	"Why haven’t you ever seen any elephants hiding up trees? Because they’re really, really good at it.",
	"I asked my North Korean friend how it was to live in North Korea. He said he can't complain.",
	"Q: How many programmers does it take to change a light bulb?\n\nA: None, that's a hardware problem.",
	"Where's the best place to hide a body?\n\nPage two of Google.",
	"I love pressing F5. It's so refreshing.",
        "Anyone can build a bridge that doesn't fall down. Only an engineer can build a bridge that just barely doesn't fall down.",
        'Three statisticians go hunting. They see a deer and the first one shoots, hitting three feet left of the deer. The second one shoots, hitting three feet right of the deer. The third one leaps up in joy, yelling, "we got him!"',
        "Standard Deviation not enough for Perverted Statistician",
        "Any salad is a Caesar salad if you stab it enough",
        "If I got $1 every time somebody called me a racist... Black people would rob me",
        "I have an EpiPen. My friend gave it to me as he was dying. It seemed very important to him that I have it.",
        "Why are gay men so well dressed?\n\nThey didn't spend all that time in the closet doing nothing.",
        "What's a pirate's least favourite letter?\n\n```Dear Sir,\nWe are writing to you because you have violated copyright...```",
        "I started a company selling land mines that look like prayer mats. Prophets are going through the roof.",
        'So a gorilla dies at a zoo right before the zoo opens. It is the only gorilla at the zoo since they are not very profitable. However, the gorilla is their most popular attraction by far, and they cannot afford to go a day without it. So the zoo owner asks one of his workers to wear a gorilla suit they have in storage for an extra $100 a day if he will go in the gorilla cage and pretend to be the gorilla until the zoo can afford a new one.\n\nQuickly, the new "gorilla" becomes the most popular craze at the zoo. People from all over are coming to see the "Human-like" gorilla. About a month in, the craze has started to wear off. So, to get peoples attention back, he decides to climb over his enclosure and hang from the net ceiling above the lions den next to him. A large crowd of people gather watching the spectacle in awe and terror. Suddenly the man loses his grip and falls to the floor of the lions den. The man starts screaming "HELP!! HELP!!!" Suddenly a lion pounces him from behind and whispers in his ear, "Shut the fuck up right now or you'+"'"+'re going to get us both fired."'
    ]

    READ_WEBSOCKET_DELAY = 1

    if slack_client.rtm_connect():
        print("Bot connected and running! " + str(AT_BOT))
        while True:
            command, channel, caller = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, caller)
            sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
