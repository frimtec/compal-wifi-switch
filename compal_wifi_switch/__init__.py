import enum


class Band(enum.Enum):
    BAND_2G = '2g'
    BAND_5G = '5g'
    ALL = 'all'

    def __str__(self):
        return self.value


class Switch(enum.Enum):
    ON = 'on'
    OFF = 'off'

    def __str__(self):
        return self.value
