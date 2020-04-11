
import json
import logging
import os
import time
import urllib
import urllib.parse
import urllib.request


class Game:

    name = 'MY_GAME'
    description = 'My Game'
    developer = 'MyGameStudios'

    @classmethod
    def _getPropsPath(cls):
        '''Return OS-specific path to the SSE props file'''
        location = 'SteelSeries Engine 3/coreProps.json'
        osPrefix = '%PROGRAMDATA%/SteelSeries/'
        return os.path.expandvars(os.path.join(osPrefix, location))

    @classmethod
    def _getProps(cls):
        '''Return SSE props json data'''
        with open(cls._getPropsPath()) as fp:
            return json.load(fp)
    
    def __init__(self):
        '''Read the props file and register the game app with SSE'''
        self.address = self._getProps()['address']
        logging.debug('SSE server at %s', self.address)

        self.register_game()

    def post(self, action, data):
        '''Handle POST request details to the SSE'''
        url = urllib.parse.urlunsplit(('http', self.address, action, '', ''))
        jsonStr = json.dumps(data).encode()
        request = urllib.request.Request(url, data=jsonStr, headers={'Content-Type': 'application/json'}, method='POST')
        logging.debug('%s | %s', request.full_url, request.data)
        response = urllib.request.urlopen(request)
        return response

    def register_game(self):
        '''Send request to register the game with SSE'''
        data= {
            'game': self.name,
            'game_display_name': self.description,
            'developer': self.developer,
        }
        return self.post('game_metadata', data)

    def remove_game(self):
        '''Send request to remove the game from SSE'''
        return self.post('remove_game', {'game': self.name})

    def heartbeat(self):
        '''Send heartbeat request to SSE in case no other event is happening for 15 seconds'''
        return self.post('game_heartbeat', {'game': self.name})

    def bind_event(self, event_type, handlers, min_value=0, max_value=100, icon_id=1, value_optional=False):
        '''Bind a new event type with a handler'''
        bindDetails = {
            'game': self.name,
            'event': event_type,
            'min_value': min_value,
            'max_value': max_value,
            'icon_id': icon_id,
            'value_optional': value_optional,
            'handlers': handlers,
        }
        return self.post('bind_game_event', bindDetails)

    def remove_event(self, event_type):
        '''Remove a particular event registered in SSE'''
        return self.post('remove_game_event', {'game': self.name, 'event': event_type})

    def event(self, event_type, value, frame=None):
        '''Send an event request of specified type to SSE'''
        eventDetails = {
            'game': self.name,
            'event': event_type,
            'data': {
                'value': value,
            },
        }
        if frame is not None:
            eventDetails['data']['frame'] = frame
        return self.post('game_event', eventDetails)


if __name__ == '__main__':
    '''Basic game that counts down progress bar on function keys and exits'''
    logging.basicConfig(level='DEBUG')
    myGame = Game()
    bar_handler = {
        'device-type': 'keyboard',
        'zone': 'function-keys',
        'color': {
            'gradient': {
                'zero': {'red': 255, 'green': 0, 'blue': 0},
                'hundred': {'red': 0, 'green': 0, 'blue': 0},
            },
        },
        'mode': 'percent',
    }

    screen_handler = {
        'device-type': 'screened',
        'zone': 'one',
        'mode': 'screen',
        'datas': [],
    }
    myGame.bind_event('HEALTH', [bar_handler])
    for ii in range(100, 0, -1):
        myGame.event('HEALTH', ii)
        time.sleep(1)
    myGame.remove_event('HEALTH')
    myGame.remove_game()

                                
    
