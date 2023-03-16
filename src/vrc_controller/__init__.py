from singletons import bus
from sounds import Audio, use_default_dictation
from osc import BotController
import time


def loop_forever():
    while True:
        time.sleep(3600)
