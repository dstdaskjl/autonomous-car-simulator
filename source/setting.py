import os, time, pathlib, logging
os.environ['KIVY_TEXT'] = 'pil'


class PreSetting:
    def load(self):
        self._configuration()

    def _configuration(self):
        from kivy.config import Config
        Config.set('graphics', 'width', '1920')
        Config.set('graphics', 'height', '1080')
        Config.set('graphics', 'fullscreen', 'False')
        Config.set('graphics', 'resizable', 'False')
        Config.set('graphics', 'maxfps', '30')
        Config.set('kivy', 'exit_on_escape', 'True')
        Config.set('kivy', 'keyboard_mode', 'systemanddock')
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

        # Wait for the configurations to be applied
        time.sleep(0.1)


class PostSetting:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

    def load(self):
        self._logger()
        self._name()
        self._path()
        self._file()

    def _file(self):
        from kivy.lang.builder import Builder
        from .simulator import Simulator

        Builder.load_file(os.path.join(self.kivy_path, 'simulator.kv'))
        self.screen_manager.add_widget(widget=Simulator(name='simulator'))

    def _logger(self):
        LoggerPatch()

    def _name(self):
        from kivy.app import App
        App.title = 'Obstacle Avoidance Simulator'

    def _path(self):
        from kivy import resources
        curr_path = os.path.dirname(__file__)
        comm_path = pathlib.Path(curr_path).parent
        resources.resource_add_path(os.path.join(comm_path, 'resource'))
        self.kivy_path = os.path.join(comm_path, 'kivy')


class LoggerPatch:
    def __init__(self):
        from kivy.logger import Logger

        self.emit_org = None
        self.oFormatter = logging.Formatter(None)

        oHandler = Logger.handlers[0]
        self.emit_org = oHandler.emit
        oHandler.emit = self._emit

    def _emit(self, record):
        ct = self.oFormatter.converter(record.created)
        t = time.strftime("%Y-%m-%d %H|%M|%S", ct)
        s = "%s.%03d: " % (t, record.msecs)

        record.msg = s + record.msg
        self.emit_org(record)
