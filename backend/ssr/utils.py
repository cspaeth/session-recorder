from django.conf import settings

keepcharacters = (' ', '.', '_')


def slugify(filename):
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


def to_container_path(path):
    return path.replace(settings.HOST_PATH, settings.BASE_PATH)