# -*- coding: utf-8 -*-

import webapp2, handlers

# Map url's to handlers
urls = [
    webapp2.Route(r'/', handler=handlers.Main, name="home"),
    webapp2.Route(r'/mail/.*', handler=handlers.emailSubmit, name="emailSubmit"),
    webapp2.Route(r'/admin', handler=handlers.Admin, name="adminPortal"),
    webapp2.Route(r'/feed', handler=handlers.imageFeed, name="imagefeed"),
    webapp2.Route(r'/add-show', handler=handlers.addShow, name="addshow"),
    webapp2.Route(r'/test-update', handler=handlers.testUpdate, name="testupdate"),
    webapp2.Route(r'/login', handler=handlers.LogIn, name="login"),
    webapp2.Route(r'/_ah/login_required', handler=handlers.LogIn),
    webapp2.Route(r'/logout', handler=handlers.LogOut, name="logout"),
    webapp2.Route(r'/account', handler=handlers.Account, name="account"),
    webapp2.Route(r'/account/setup', handler=handlers.AccountSetup, name="setup"),
    (r'.*', handlers.NotFound)
]
