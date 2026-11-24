# -*- coding: utf-8 -*-
"""Experimental device-OAuth compatibility based on the supplied Taapat IPK.

This module is used by the separate testing branch. No user tokens or
passwords are shipped. The consent identity belongs to the OAuth project
configured below, not to the Warder project.
"""
def get_key(x):
    p = 3
    while True:
        if p > len(x):
            break
        pl = len(str(p))
        x = x[:p] + x[p + pl:]
        p += 12 - pl
    x = x.replace('w_OizD', 'a')
    x = x.replace('Xhi_Lo', 'A')
    return x

COMPAT_CLIENT_ID = get_key('4113447027255-v15bgs05u1o3m278mpjs2vcd0394w_OizDfrg5160drbw_Oiz63D.w_OizDpp75s.googleus87ercontent.99com')
COMPAT_CLIENT_SECRET = get_key('Zf93pqd2rxgY2ro159rK20BMxif27')
COMPAT_SCOPE = "https://www.googleapis.com/auth/youtube"
COMPAT_DEVICE_URL = "https://accounts.google.com/o/oauth2/device/code"
COMPAT_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
COMPAT_DEVICE_GRANT = "http://oauth.net/grant_type/device/1.0"


def compatibility_client():
    """One codepath for new TV codes and subsequent refreshes."""
    return {
        "client_id": COMPAT_CLIENT_ID,
        "client_secret": COMPAT_CLIENT_SECRET,
        "scope": COMPAT_SCOPE,
        "device_url": COMPAT_DEVICE_URL,
        "token_url": COMPAT_TOKEN_URL,
        "device_grant": COMPAT_DEVICE_GRANT,
    }
