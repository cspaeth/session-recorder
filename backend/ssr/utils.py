from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

keepcharacters = (' ', '.', '_')


def slugify(filename):
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


def to_container_path(path):
    return path.replace(settings.HOST_PATH, settings.BASE_PATH)


def send_to_channel(name, message, data):
    # print("sending to channel %s (%s): %s" % (name, message, data))
    async_to_sync(get_channel_layer().send)(name, {
        'type': message,
        'data': data
    })


def send_to_group(name, message, data):
    # print("sending to group %s (%s): %s" % (name, message, data))
    async_to_sync(get_channel_layer().group_send)(name,
        {
            'type': message,
            'data': data
        }
    )