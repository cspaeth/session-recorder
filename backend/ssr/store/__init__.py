from ssr.store.auth import Authentication
from ssr.store.recorder import ReaperRecorder
from ssr.store.session import SessionControl
from ssr.store.util import ApplicationStore

store = ApplicationStore()

recorder = ReaperRecorder()
session = SessionControl(recorder)
auth = Authentication()

store.register_module(auth, 'ACTIVE_USER')
store.register_module(session, 'SESSION')
store.register_module(recorder, 'RECORDER')
