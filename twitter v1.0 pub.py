import tweepy
import json
import re
import time

auth = tweepy.OAuthHandler('xxxx', 'xxxx')
auth.set_access_token('xxxx',
                      'xxxx')

api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

message_received_list = []

class My_Stream_Listener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

    #for receiving, processing, and sending information
    def on_data(self, status):
        #getting message information and converting to JSON
        direct_messages_tweepy = api.direct_messages()
        direct_messages_json = json.dumps(direct_messages_tweepy)
        dm_json_for_processing = json.loads(direct_messages_json)

        #processing JSON data for information needed to read text
        dm_as_dict = dm_json_for_processing[0]
        message_received = dm_as_dict.get('text', 0)

        try:
            #usuing regex search to find information in the users message
            match_item_cost_name = re.findall(r'(?:^|\W)cost(?:$|\W)', message_received, re.IGNORECASE)[0]
            match_item_cost_amount = re.findall(r'\d+\.+\d*', message_received)[0]
            match__paid__name = re.findall(r'(?:^|\W)paid(?:$|\W)', message_received, re.IGNORECASE)[0]
            match_paid_amount = re.findall(r'\d+\.+\d*', message_received)[1]

            #taking the information pulled through the regex search and determining postions of information in message
            positionn_of_cost_name = message_received.find(match_item_cost_name) + 1
            position_of_cost_amount = message_received.find(str(match_item_cost_amount))
            positionn_of_paid_name = message_received.find(match__paid__name) + 1
            position_of_paid_amount = message_received.find(str(match_paid_amount))

            #determining if the message received meets the correct positioning format
            if positionn_of_cost_name < position_of_cost_amount < positionn_of_paid_name < position_of_paid_amount:
                True
            else:
                message_number = dm_as_dict.get('id', 0)
                user_id_received = dm_as_dict.get('sender_screen_name', 0)
                length_of_message_list = len(message_received_list)
                message_received_list.append(message_number)
                if message_received_list[length_of_message_list] == message_received_list[length_of_message_list - 1]:
                    return True
                else:
                    #right now I have to use 'cool downs' for the message being sent by the bot so Twitter doesn't do a temp suspension 
                    time.sleep(5)
                    api.send_direct_message(screen_name=user_id_received,
                                            text="Make sure your message is formatted in the correct order ")
                    time.sleep(5)
                    api.send_direct_message(screen_name=user_id_received, text="Cost: XX.XX Paid: XX.XX")

            items_new = float(match_item_cost_amount)
            items = []
            change_due_list = []
            items.append(items_new)

            #determines the difference between the purchase price and amount paid
            def register(cost, payment):
                item = items[0]
                return float("{0:.2f}".format(payment - item))

            #calculates change for the item purchased and amount paid
            def change_machine(change):
                change = float("{0:.2f}".format(change))
                if (change <= 0.0):
                    return
                elif (change >= 20):
                    bills = 0
                    while (change >= 20):
                        bills += 1
                        change -= 20
                    change_due_list.append(str(bills) + ' $20 dollar bills')
                    return change_machine(change)
                elif (change >= 10):
                    bills = 0
                    while (change >= 10):
                        bills += 1
                        change -= 10
                    change_due_list.append(str(bills) + ' $10 dollar bills')
                    return change_machine(change)
                elif (change >= 5):
                    bills = 0
                    while (change >= 5):
                        bills += 1
                        change -= 5
                    change_due_list.append(str(bills) + ' $5 dollar bills')
                    return change_machine(change)
                elif (change >= 1):
                    bills = 0
                    while (change >= 1):
                        bills += 1
                        change -= 1
                    change_due_list.append(str(bills) + ' $1 dollar bills')
                    return change_machine(change)
                elif (change >= 0.25):
                    coins = 0
                    while (change >= .25):
                        coins += 1
                        change -= 0.25
                    change_due_list.append(str(coins) + ' quarters')
                    return change_machine(change)
                elif (change >= 0.10):
                    coins = 0
                    while (change >= .10):
                        coins += 1
                        change -= 0.10
                    change_due_list.append(str(coins) + ' dimes')
                    return change_machine(change)
                elif (change >= 0.05):
                    coins = 0
                    while (change >= .05):
                        coins += 1
                        change -= 0.05
                    change_due_list.append(str(coins) + ' nickles')
                    return change_machine(change)
                elif (change >= 0.01):
                    coins = 0
                    while (change >= .01):
                        coins += 1
                        change -= 0.01
                    change_due_list.append(str(coins) + ' pennies')
                    return change_machine(change)

            #test to ensure the amount paid is greater than the items cost. If this test fails the sender is notified
            item_to_buy = float(items[0])
            payment = float(match_paid_amount)
            while payment < item_to_buy:
                message_number = dm_as_dict.get('id', 0)
                user_id_received = dm_as_dict.get('sender_screen_name', 0)
                length_of_message_list = len(message_received_list)
                message_received_list.append(message_number)
                if message_received_list[length_of_message_list] == message_received_list[length_of_message_list - 1]:
                    return True
                else:
                    time.sleep(5)
                    api.send_direct_message(screen_name=user_id_received,
                                            text="That's not enough money, please reenter the amount your going to pay")
                payment = float(match_paid_amount)

            #passing the register function, the cost of the item being purchased and the amount paid
            change = (register(item_to_buy, payment))
            change_machine(change)

            change_due_reply = 'Your change is: $' + str(change)

            #sending the user their change
            message_number = dm_as_dict.get('id', 0)
            user_id_received = dm_as_dict.get('sender_screen_name', 0)
            length_of_message_list = len(message_received_list)
            message_received_list.append(message_number)
            if message_received_list[length_of_message_list] == message_received_list[length_of_message_list - 1]:
                return True
            else:
                time.sleep(5)
                api.send_direct_message(screen_name=user_id_received, text=change_due_reply)
                for i in range(len(change_due_list)):
                    time.sleep(5)
                    api.send_direct_message(screen_name=user_id_received, text=change_due_list[i])

        #if the message received isn't in the right format, this exception will informthe sender and tell them the right format
        except Exception as e:
            message_number = dm_as_dict.get('id', 0)
            user_id_received = dm_as_dict.get('sender_screen_name', 0)
            length_of_message_list = len(message_received_list)
            message_received_list.append(message_number)
            if message_received_list[length_of_message_list] == message_received_list[length_of_message_list - 1]:
                return True
            else:
                time.sleep(5)
                api.send_direct_message(screen_name=user_id_received, text='Please use the following format for the cash register ')
                time.sleep(5)
                api.send_direct_message(screen_name=user_id_received, text="Cost: XX.XX Paid: XX.XX")
        return True

    #function for returning twitter errors
    def on_error(self, status_code):
        if status_code == 420:
            return False

my_stream_listener = My_Stream_Listener()
my_stream = tweepy.Stream(auth=api.auth, listener=my_stream_listener)
my_stream.userstream()