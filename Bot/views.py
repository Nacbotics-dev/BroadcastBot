import telebot,json,ast,urllib
from .models import Channel,STEP
from django.conf import settings
from django.http import HttpResponse
from .misc import get_channel_info_from_dict,channel_data
from django.views.decorators.http import require_http_methods
from .Keyboards import available_channels,confirmBroadcast,urlKeyboard



bot = telebot.TeleBot(settings.WEBHOOK_TOKEN,parse_mode='HTML') #Telegram Bot API


def user_details(message):
	detail = {}
	detail["chat_id"] = message.chat.id
	detail["msg_type"] = message.chat.type
	detail["user_id"] = message.from_user.id
	detail["username"] = message.from_user.username
	return(detail)

def returnChannel(ChannelId):
    channel = Channel.objects.get(ChannelId__contains=ChannelId)

    return(channel.chat_name)

def MessageChannel(userID):
    UserState = return_state(userID)

    channel = Channel.objects.get(ChannelId__contains=UserState['channelID'])

    button_name = UserState['button_name']
    url_link = UserState['url_link']

    bot.send_message(channel.chat_id,UserState['msg'],reply_markup=urlKeyboard(button_name,url_link))

def MessageChannelPhoto(userID):
    UserState = return_state(userID)

    channel = Channel.objects.get(ChannelId__contains=UserState['channelID'])

    button_name = UserState['button_name']
    url_link = UserState['url_link']
    photo = UserState['photo']
    bot.send_photo(channel.chat_id,caption=UserState['msg'],photo=urllib.request.urlopen(photo).read(),reply_markup=urlKeyboard(button_name,url_link))

def return_state(user):
    """ Returns the current state of a user """

    # save our user's state instance
    my_state, created = STEP.objects.get_or_create(user = user)
    if created == True:
        my_state.state ="{}"
        my_state.save()
        STEP.objects.filter(user = user).update(next_step="")
    else:
        pass

    MY_STEP = STEP.objects.get(user=user)
    try:
        MY_STATE = ast.literal_eval(MY_STEP.state)#.replace('"',"'")
    except Exception as e:
        print("STEP ERROR :",e)
        MY_STATE = dict()
        
    return(MY_STATE)


@bot.message_handler(commands=['start'])
def start(message):
    report = None
    user_detail = user_details(message)
    
    if user_detail["msg_type"] == "private":
        step,created = STEP.objects.get_or_create(user=user_detail['user_id'])
        bot.send_message(user_detail['chat_id'],'Welcome gracious user 😇')

@bot.message_handler(commands=['broadcast'])
def registerBot(message):
    report = None
    user_detail = user_details(message)
    
    if user_detail["msg_type"] == "private":
        channels = Channel.objects.filter(chat_admin=user_detail['user_id']).all()
        print(channels)
        bot.send_message(user_detail['chat_id'],'<b> Please Select The channel To Message Send To </b>',reply_markup=available_channels(channels))
   
@bot.message_handler(content_types=['text'])
def reply_msg(message):
    user_detail = user_details(message)
    if user_detail["msg_type"] == "private":
        step,created = STEP.objects.get_or_create(user=user_detail['user_id'])
        UserState = return_state(user_detail['user_id'])

        if step.next_step == 'EnterMessage':
            UserState.update({'msg':message.text})
            STEP.objects.filter(user = user_detail['user_id']).update(next_step='EnterUrl',state = UserState)

            bot.send_message(user_detail['chat_id'],f'<b>Enter URL in this order</b>: \n\n (button_name)+(url) \n\n without the brackets')

        elif step.next_step == 'EnterUrl':

            try:
                text = message.text.replace('(','').replace(')','')
                button_name = text.split('+')[0]
                url_link = text.split('+')[1]
                UserState.update({'button_name':button_name,'url_link':url_link})

                msg = f"""

                <b>Message To: </b> <i>{returnChannel(UserState['channelID'])}</i>

                \n\n

                <b>Message Body:</b>

                {UserState['msg']}
                
                """

                STEP.objects.filter(user = user_detail['user_id']).update(next_step='',state = UserState)
                bot.send_message(user_detail['chat_id'],msg,reply_markup=confirmBroadcast())
            except Exception as e:
                print(e,'@@@@@@@@')
                bot.send_message(user_detail['chat_id'],f'<b>Enter URL in this order</b>: \n\n (button_name)+(url) \n\n without the brackets')
            
            
    else:
        pass

@bot.message_handler(content_types=["photo"])
def get_photo(message):
    user_detail = user_details(message)
    # user = User.objects.get(user_id=user_detail['user_id'])
    fileID = message.photo[-1].file_id
    photo = bot.get_file_url(fileID)

    if user_detail["msg_type"] == "private":
        step,created = STEP.objects.get_or_create(user=user_detail['user_id'])
        UserState = return_state(user_detail['user_id'])

        if step.next_step == 'EnterMessage':
            UserState.update({'msg':message.caption,'photo':photo})
            STEP.objects.filter(user = user_detail['user_id']).update(next_step='EnterUrl',state = UserState)

            bot.send_message(user_detail['chat_id'],f'<b>Enter URL in this order</b>: \n\n (button_name)+(url) \n\n without the brackets')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        userID = call.from_user.id
        chat_id = call.message.chat.id
        UserState = return_state(userID)
        if call.data.startswith('to:'):
            channelID = hex(int(call.data.split(':')[1]))[2:]
            UserState.update({'channelID':channelID})
            STEP.objects.filter(user=userID).update(next_step='EnterMessage',state = UserState)
            bot.edit_message_text(chat_id=chat_id, text='<b> Please enter the text you want to send</b>', message_id=call.message.message_id)
        
        elif call.data == 'confirm':

            photo = UserState.get('photo')
            if photo:
                MessageChannelPhoto(userID)
            else:
                MessageChannel(userID)


            STEP.objects.filter(user=userID).update(next_step='',state = '')
            bot.edit_message_text(chat_id=chat_id, text='<b> Message Sent ✅✅</b>', message_id=call.message.message_id)

    except Exception as e:
        print(f"CALLBACK ERROR : {e}")
        pass

@require_http_methods(["GET","POST"])
# @RateLimiter(max_calls=100, period=1)
def WebConnect(request):
	# Listens only for GET and POST requests
	# returns django.http.HttpResponseNotAllowed for other requests
	# Handle the event appropriately

    if request.method == 'POST':
        jsondata = request.body
        data = json.loads(jsondata)
        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])

        try:
            ## THIS MONITORS WHEN THE HAS BEEN ADDED TO A GROUP/CHANNEL
            new_update = list(data.keys())[1]
            my_chat_member = data[new_update]
            user_detail = get_channel_info_from_dict(my_chat_member)
            if user_detail['status'] == 'administrator' and user_detail['bot'] == True and user_detail['bot_id'] == int(settings.BOT_ID):
                channel,created = Channel.objects.get_or_create(chat_id=user_detail['channel_id'],chat_name=user_detail['channel_name'],chat_admin=user_detail['user_id'])
                bot.send_message(user_detail['channel_id'],'Glad to be here 😇')
            
        except Exception as e:
            print(e)
        return HttpResponse(status=201)
    else:
        bot.remove_webhook()
        bot.set_webhook(url=settings.WEBHOOK_URL+settings.WEBHOOK_TOKEN)
        return HttpResponse(status=201)
