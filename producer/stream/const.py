from enum import StrEnum

class StreamMode(StrEnum):
    LIVE = 'live'
    PLAYBACK = 'playback'
    IDLE = 'idle'
    FILE = 'file'
