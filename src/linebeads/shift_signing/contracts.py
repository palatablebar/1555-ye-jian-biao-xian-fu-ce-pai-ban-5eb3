from linebeads.retrocheck_slots.midshift import *  # noqa: F401,F403
from linebeads.retrocheck_slots import midshift as _core

def __getattr__(name):
    return _core.__getattr__(name)
