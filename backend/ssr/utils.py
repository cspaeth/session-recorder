from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_to_channel(name, message, data):
    # print("sending to channel %s (%s): %s" % (name, message, data))
    async_to_sync(get_channel_layer().send)(name, {
        'type': message,
        'data': data
    })


def send_to_group(name, message, data):
    # print("sending to group %s (%s): %s" % (name, message, data))
    async_to_sync(get_channel_layer().group_send)(name, {
        'type': message,
        'data': data
    })
