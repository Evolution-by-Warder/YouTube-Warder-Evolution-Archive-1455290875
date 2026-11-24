# -*- coding: utf-8 -*-
"""Bundled device sign-in profile for YouTube Warder Evolution.

This is an application configuration. It does not contain user tokens,
passwords, or account history.
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

TV_CLIENT_ID = get_key('4113447027255-v15bgs05u1o3m278mpjs2vcd0394w_OizDfrg5160drbw_Oiz63D.w_OizDpp75s.googleus87ercontent.99com')
TV_CLIENT_SECRET = get_key('Zf93pqd2rxgY2ro159rK20BMxif27')
TV_SCOPE = "https://www.googleapis.com/auth/youtube"
TV_DEVICE_URL = "https://accounts.google.com/o/oauth2/device/code"
TV_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
TV_DEVICE_GRANT = "http://oauth.net/grant_type/device/1.0"


def bundled_tv_client():
    """One codepath for new TV codes and subsequent refreshes."""
    return {
        "client_id": TV_CLIENT_ID,
        "client_secret": TV_CLIENT_SECRET,
        "scope": TV_SCOPE,
        "device_url": TV_DEVICE_URL,
        "token_url": TV_TOKEN_URL,
        "device_grant": TV_DEVICE_GRANT,
    }
