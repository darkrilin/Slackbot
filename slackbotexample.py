import os
import time
from slackclient import SlackClient


# starterbot's ID as an environment variable
BOT_ID = os.environ.get('SLACK_BOT_ID', 'U1WBVJF8A')
AT_BOT = "<@" + str(BOT_ID) + ">:"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "I don't understand"
    if command.startswith('test'):
        response = "Hello, World!"
    else:
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        if output_list[0]['type'] != 'reconnect_url':
            print(output_list)
            print('')
        for output in output_list:
            if 'text' in output and AT_BOT in output['text']:
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print("BroBot connected and running! " + str(AT_BOT))
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
        print("Disconnected")
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
