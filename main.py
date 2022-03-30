from source.setting import PreSetting, PostSetting
PreSetting().load()

from kivy.uix.screenmanager import ScreenManager, NoTransition
screen_manager = ScreenManager(transition=NoTransition())
PostSetting(screen_manager=screen_manager).load()

from kivy.app import App
from kivy.logger import Logger


class Application(App):
    def build(self):
        return screen_manager


def main():
    try:
        Application().run()
    except (KeyboardInterrupt, SystemExit):
        Logger.exception(msg='Exception:')
    finally:
        Logger.info(msg='Exit: HMI has been closed')


if __name__ == '__main__':
    main()
