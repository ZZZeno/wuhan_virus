import sys

from flask_script import Manager, Server as _Server
from app import app
from config import Config
from cron import get_data
from flask_apscheduler import APScheduler

scheduler = APScheduler()

class Server(_Server):

    def __call__(self, app, host, port, use_debugger, use_reloader,
                 threaded, processes=None, passthrough_errors=None, ssl_crt=None, ssl_key=None):
        # we don't need to run the server in request context
        # so just run it directly
        self.scheduler_init(app)

        if use_debugger is None:
            use_debugger = app.debug
            if use_debugger is None:
                use_debugger = True
                if sys.stderr.isatty():
                    print("Debugging is on. DANGER: Do not allow random users to connect to this server.")
        if use_reloader is None:
            use_reloader = use_debugger

        if None in [ssl_crt, ssl_key]:
            ssl_context = None
        else:
            ssl_context = (ssl_crt, ssl_key)

        app.run(host=host,
                port=port,
                debug=use_debugger,
                use_debugger=use_debugger,
                use_reloader=use_reloader,
                threaded=threaded,
                processes=processes,
                passthrough_errors=passthrough_errors,
                ssl_context=ssl_context,
                **self.server_options)

    def scheduler_init(self, app):
        # scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.add_job('scheduler_task', get_data, trigger='cron', minute='*/10',
                          replace_existing=True)
        scheduler.start()


manager = Manager(app)

manager.add_command('debug', Server(host='0.0.0.0', port=20201, use_debugger=True, threaded=True, use_reloader=True))
manager.add_command('product', Server(host='0.0.0.0', port=20201, threaded=True))

if __name__ == '__main__':
    manager.run()
