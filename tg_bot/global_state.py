_user_tokens = {}
_user_notifications = {}
_user_state = {}


def get_user_tokens():
    return _user_tokens


def get_user_notifications():
    return _user_notifications


def get_user_state():
    return _user_state


def set_user_token(chat_id, token):
    _user_tokens[chat_id] = token


def remove_user_token(chat_id):
    _user_tokens.pop(chat_id, None)


def set_user_notification(chat_id, notification_id):
    _user_notifications[chat_id] = notification_id


def remove_user_notification(chat_id):
    _user_notifications.pop(chat_id, None)


def set_user_state(chat_id, state):
    _user_state[chat_id] = state


def get_user_state_by_chat_id(chat_id):
    return _user_state.get(chat_id)


def remove_user_state(chat_id):
    _user_state.pop(chat_id, None)
