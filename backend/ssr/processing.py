import os
from os import path
from pathlib import Path

import dropbox
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.layers import get_channel_layer
from django.conf import settings
from dropbox.exceptions import ApiError
from dropbox.files import GetMetadataError
from pydub import AudioSegment

from ssr.apps.models.models import Session, Take
from ssr.utils import to_container_path


class UploadProcessor(SyncConsumer):

    def upload_session(self, message):
        session = Session.objects.get(pk=message['session_id'])
        print(session)
        for take in session.takes.filter(state="queued"):
            take.processing_started()
            take.save()
            async_to_sync(get_channel_layer().group_send)(
                settings.SESSION_ROOM_NAME,
                {
                    'type': 'session_update',
                }
            )

            self.upload_file(take.id)

            take.upload_finished()
            take.save()

            async_to_sync(get_channel_layer().group_send)(
                settings.SESSION_ROOM_NAME,
                {
                    'type': 'session_update',
                }
            )

        #
        #

    def upload_file(self, take_id):
        take = Take.objects.get(pk=take_id)

        project_file = to_container_path(take.session.project_file)
        project_dir = path.dirname(project_file)
        uploads_folder = path.join(project_dir, "uploads")

        Path(uploads_folder).mkdir(parents=True, exist_ok=True)

        target_filename = "Take {:02d} - {}.mp3".format(take.number, take.name)
        target_file = path.join(uploads_folder, target_filename)

        AudioSegment.from_file(to_container_path(take.take_mix_source)).export(target_file, format='mp3')
#
        (profile, session) = project_dir.split(os.sep)[-2:]
        db_path = "/{}/{}".format(profile, session)
        db_file = "{}/{}".format(db_path, target_filename)

        with dropbox.Dropbox(settings.DROPBOX_TOKEN) as db:
            self.ensure_path_exists(db, db_path)

            with open(target_file, 'rb') as f:
                db.files_upload(f.read(), db_file)


    def ensure_path_exists(self, db, db_path):
        current_path = ""
        for dir in db_path.split("/")[1:]:
            current_path += "/{}".format(dir)
            try:
                db.files_get_metadata(current_path)
            except ApiError as e:
                if isinstance(e.error, GetMetadataError):
                    db.files_create_folder(current_path)
                else:
                    raise


