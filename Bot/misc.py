

def get_channel_info_from_dict(data):
    detail = {}
    detail["channel_id"] = data['chat']['id']
    detail["channel_name"] = data['chat']['title']
    detail["channel_type"] = data['chat']['type']

    
    detail["user_id"] = data['from']['id']
    detail["username"] = data['from']['username']

    if data['chat']['type'] == 'channel':
        detail["bot_name"] = data['new_chat_member']['user']['username']
        detail["bot_id"] = data['new_chat_member']['user']['id']
        detail['status'] = data['new_chat_member']['status']
        detail['bot'] = data['new_chat_member']['user']['is_bot']
    
    if 'group' in data['chat']['type']:
        detail["bot_name"] = data['new_chat_participant']['username']
        detail["bot_id"] = data['new_chat_participant']['id']
        detail['bot'] = data['new_chat_participant']['is_bot']
        detail['status'] = 'administrator'

    return(detail)

    

def channel_data(message):
    detail = {}
    detail["channel_id"] = message.chat.id
    detail["channel_name"] = message.chat.title
    detail["channel_type"] = message.chat.type
    detail["user_id"] = message.from_user.id
    detail["username"] = message.from_user.username
    detail["bot_name"] = message.json['new_chat_participant']['username']
    detail["bot_id"] = message.json['new_chat_participant']['id']

    return(detail)