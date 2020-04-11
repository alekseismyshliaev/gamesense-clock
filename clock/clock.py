''' System Clock app for SteelSeries Engine

Intended to post clock (HH:MM) every second to SSE
to display on the OLED screen (Apex keyboard)

=======
Credits
=======

Python 3.8
Pillow
Pystray
SteelSeries GameSense API

'''
import datetime
import logging
import time

from   PIL import Image, ImageDraw
from   pystray import Icon, Menu, MenuItem


from base import Game


class Clock(Game):
    ''' Clock integration for the SSE OLED display '''

    name = 'SYSTEM_CLOCK'
    description = 'System Clock app for OLED display'
    developer = 'Aleksei Smyshliaev'

    minute_event_name = 'MINUTE'

    is24h = True
    format_12h = '%I:%M %p'
    format_24h = '%H:%M'

    shutdown = False

    @property
    def time_format(self):
        if self.is24h:
            return self.format_24h
        else:
            return self.format_12h

    def __init__(self):
        '''Initialize and bind the minute tick event'''
        super().__init__()

        screen_handler = {
            'device-type': 'screened',
            'zone': 'one',
            'mode': 'screen',
            'datas': [
                {
                    'has-text': True,
                    'bold': True,
                    'context-frame-key': 'time',
                },
            ],
        }                

        logging.info('binding SSE event')
        # ``value_optional`` means every event will get processed
        # disregarding the numerical value passed in the event
        self.bind_event(self.minute_event_name, [screen_handler], value_optional=True)

    def main_loop(self):
        '''Main loop to send timestamp updates to SSE'''
        old_ts = ''
        try:
            while True:
                new_ts = datetime.datetime.now().strftime(self.time_format)
                if new_ts != old_ts:
                    # send value as ``1``, because we use context-frame
                    self.event(self.minute_event_name, 1, {'time': new_ts})
                    old_ts = new_ts
                else:
                    # send heartbeat if nothing else is happening
                    self.heartbeat()
                time.sleep(1)
                if self.shutdown:
                    break
        finally:
            self.remove_event(self.minute_event_name)
            self.remove_game()

    def __call__(self):
        self.icon = self.create_icon()
        self.icon.run(self.pystraySetup)

    ### pystray
        
    def pystraySetup(self, icon):
        '''Callable to execute in a second thread for the pystray Icon'''
        logging.info('starting systray icon')
        # Setting ``icon.visible`` is mandatory for custom setup functions
        icon.visible = True
        # Run the event mainloop here,
        # because pystray has to be run in the main thread
        self.main_loop()
        # after main loop is done ask pystray to stop
        icon.stop()
        logging.info('shutting down systray icon')
        
    def create_icon(self):
        '''Initialize pystray object '''
        icon = Icon(
            name='System Clock for SSE',
            title='System Clock integration for SteelSeriesEngine OLED',
            icon=self.create_image(),
            menu=self.create_menu(),
        )
        return icon

    def create_image(self):
        '''Construct image for the pystray object'''
        logging.info('loading favicon.ico')
        image = Image.open('favicon.ico')
        image.load()
        image.convert('RGB')
        return image

    def create_menu(self):
        '''Construct context menu for the pystray object'''
        logging.info('construction menu')
        def on_change_format(icon, item):
            self.is24h = not item.checked
            logging.info('menu: 24h format (%s)', self.is24h)

        def get_format(item):
            return self.is24h

        format_item = MenuItem(
            '24h format',
            on_change_format,
            checked=get_format,
        )

        def on_quit(icon, item):
            logging.info('menu: quit')
            self.shutdown = True
        
        quit_item = MenuItem(
            'Quit',
            on_quit,
            default=True,
        )

        menu = Menu(*(
            format_item,
            Menu.SEPARATOR,
            quit_item,
        ))
        return menu


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    c = Clock()()
