from ssr.store.auth import Authentication
from ssr.store.recorder import ReaperRecorder
from ssr.store.session import SessionControl
from ssr.store.sessions import SessionArchive
from ssr.store.util import ApplicationStore

store = ApplicationStore()

recorder = ReaperRecorder()
auth = Authentication()
session = SessionControl(recorder, auth)
sessions = SessionArchive(auth)
store.register_module(auth, 'ACTIVE_USER')
store.register_module(session, 'SESSION')
store.register_module(recorder, 'RECORDER')
store.register_module(sessions, 'SESSIONS')