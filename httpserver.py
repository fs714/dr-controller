from eventlet import wsgi
import eventlet
from urlrecorder import record_url

app = record_url()
wsgi.server(eventlet.listen(('', 80)), app)

