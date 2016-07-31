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
    if command.startswith('debug_response'):
        response = "This is a testy test"
    elif command.startswith('debug_question_standard'):
        response = ' , '.join(RANDOM)
    elif command.startswith('debug_users'):
        pprint(get_users())
        response = ""
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
def get_users(justnames=True):
    userlist = slack_client.api_call('users.list', token=debug_token)
    if justnames == True:
        namelist = []
        for i in userlist['members']:
            print(i['name'], i['id'])
        return ""
    else:
        return userlist


# MAIN
if __name__ == "__main__":
    BOT_ID = os.environ.get('SLACK_BOT_ID', 'U1WBVJF8A')
    AT_BOT = "<@" + str(BOT_ID) + ">"

    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    debug_token = os.environ.get('SLACK_TEST_TOKEN')

    CONFUSED = [
        "I'm not really sure what you mean", "I'm not sure what you're saying", "I don't understand",
        "What do you mean?", "I'm not sure I understand", "What are you saying?", "Huh?", "¯\_(ツ)_/¯",
        "What are you trying to say?", "What does that mean?", "Could you explain?", "What?"
    ]
    PUNCTUATION = ['.',',','?','!',"'",';']
    
    READ_WEBSOCKET_DELAY = 1
    
    if slack_client.rtm_connect():
        print("Bot connected and running! " + str(AT_BOT))
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
