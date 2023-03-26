import configparser
from typing import List

CITY = {
    u"limassol": "/lemesos-district-limassol/",
    u"pafos": "/pafos-district-paphos/"
}

FURNISHING = {
    u"1": "/furnishing---1/",
    u"0": "/furnishing---3/"
}


class Config:
    def __init__(self):
        self.filename = 'config.ini'
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    @property
    def bazaraki_url(self):
        self.config.read(self.filename)
        return self.config['source']['bazaraki']

    @property
    def telegram_channels(self) -> List[int]:
        self.config.read(self.filename)
        return [int(channel_id) for channel_id in self.config['source']['telegram'].split(',')]

    @property
    def min_price(self):
        self.config.read(self.filename)
        return int(self.config['requirements']['min_price'])

    @property
    def max_price(self):
        self.config.read(self.filename)
        return int(self.config['requirements']['max_price'])

    @property
    def city(self):
        self.config.read(self.filename)
        return CITY[self.config['requirements']['city']]

    @property
    def furnishing(self):
        self.config.read(self.filename)
        return FURNISHING[self.config['requirements']['furnishing']]

    @property
    def min_rooms(self):
        self.config.read(self.filename)
        return int(self.config['requirements']['min_rooms'])

    @property
    def max_rooms(self):
        self.config.read(self.filename)
        return int(self.config['requirements']['max_rooms'])

    @property
    def count_photo(self):
        return int(self.config['bot']['count_photo'])

    @property
    def interval(self):
        return int(self.config['bot']['interval'])

    @property
    def clearing(self):
        return int(self.config['bot']['clearing'])


def get_bedrooms():
    config = Config()
    return '/'.join(f'number-of-bedrooms---{str(i)}' for i in range(config.min_rooms, config.max_rooms + 1))
