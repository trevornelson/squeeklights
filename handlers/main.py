# -*- coding: utf-8 -*-
import os
import logging
import webapp2
import json
import datetime

from hashlib import md5
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import mail

# Import packages from the project
import mc
import tools.mailchimp
import time
import instagram

from models import *
from baserequesthandler import BaseRequestHandler
from tools.common import decode
from tools.decorators import login_required, admin_required



# OpenID login
class LogIn(BaseRequestHandler):
    """
    Redirects a user to the OpenID login site. After successful login the user
    redirected to the target_url (via /login?continue=/<target_url>).
    """
    def get(self):
        # Wrap target url to redirect new users to the account setup step
        target_url = "/account?continue=%s" % \
                decode(self.request.get('continue'))

        action = decode(self.request.get('action'))
        if action and action == "verify":
            fid = decode(self.request.get('openid_identifier'))
            url = users.create_login_url(target_url, federated_identity=fid)
            self.redirect(url)
        else:
            # BaseRequestHandler provides .render() for rendering a template
            self.render("login.html", {"continue_to": target_url})


# LogOut redirects the user to the GAE logout url, and then redirects to /
class LogOut(webapp.RequestHandler):
    def get(self):
        url = users.create_logout_url("/")
        self.redirect(url)

# Handler used to initiate test feed update
class testUpdate(BaseRequestHandler):
    def get(self):
        client_id='8393870dc08f47348d92bb0a759d0aa8'
        client_secret='3cc856fcf7f74ed09af7052f0710ad15'
        current_time = time.time()        

        api = instagram.client.InstagramAPI(client_id=client_id, client_secret=client_secret)
        v = Venue.all().filter("status =", "unfetched").fetch(1000)
        shows = list(v)
        image_urls = []

        for show in shows:
            int_end_time = int(show.end_time)
            if int_end_time < current_time:
                latitude = show.latitude
                longitude = show.longitude
                start_time = show.start_time
                end_time = show.end_time
                geo_media = api.media_search(lat=latitude, lng=longitude, min_timestamp=start_time, max_timestamp=end_time, distance=75)
                for media in geo_media:
                    image = media.images['standard_resolution'].url
                    image_urls.append(image)
                show.status = 'fetched'
                show.images = image_urls  # Update by adding new image table, linking to specific show and giving each image a unique ID
                show.put()

        self.redirect("/")


# Main page request handler
class Main(BaseRequestHandler):
    def get(self):
        self.render("index.html")


# Email submit page request handler
class emailSubmit(BaseRequestHandler):
    def post(self):
        sender_address = "trevor.nelson1@gmail.com"
        recipient_address = "trevor.nelson.marketing@gmail.com"
        subject = "New Contact Submission"
        name = self.request.get("name")
        phone = self.request.get("phone")
        email = self.request.get("email")
        message = self.request.get("message")

        body = """
        Name: %s
        Phone: %s
        Email: %s

        %s
        """ % (name, phone, email, message)

        mail.send_mail(sender_address, recipient_address, subject, body)

        self.redirect("/%s") % sender_address


class imageFeed(BaseRequestHandler):
    def get(self):
        v = Venue.all().filter("status =", "fetched").fetch(1000)
        shows = list(v)
        image_urls = []

        for show in shows:
            for image in show.images:
                image_urls.append(image)

        template_dict = {'image_urls':image_urls}
        self.render("feed.html", template_dict)

class addShow(BaseRequestHandler):
    def get(self):
        # Google Places search bar
        self.render("index.html")

    def post(self):
        venue_name = self.request.get("venue_name")
        band_name = self.request.get("band")
        longitude = self.request.get("longitude")
        latitude = self.request.get("latitude")
        start_time = self.request.get("start_timestamp")
        end_time = self.request.get("end_timestamp")
        status = "unfetched"

        p = Venue(venue_name=venue_name,
                    band_name=band_name,
                    longitude=longitude,
                    latitude=latitude,
                    start_time=start_time,
                    end_time=end_time,
                    status=status)
        p.put()
        self.redirect("/add-show")



# Account page and after-login handler
class Account(BaseRequestHandler):
    """
    The user's account and preferences. After the first login, the user is sent
    to /account?continue=<target_url> in order to finish setting up the account
    (email, username, newsletter).
    """
    def get(self):
        target_url = decode(self.request.get('continue'))
        # Circumvent a bug in gae which prepends the url again
        if target_url and "?continue=" in target_url:
            target_url = target_url[target_url.index("?continue=") + 10:]

        if not self.userprefs.is_setup:
            # First log in of user. Finish setup before forwarding.
            self.render("account_setup.html", {"target_url": target_url, 'setup_uri':self.uri_for('setup')})
            return

        elif target_url:
            # If not a new user but ?continue=<url> supplied, redirect
            self.redirect(target_url)
            return

        # Render the account website
        self.render("account.html", {'setup_uri':self.uri_for('setup')})


class AccountSetup(BaseRequestHandler):
    """Initial setup of the account, after user logs in the first time"""
    def post(self):
        username = decode(self.request.get("username"))
        email = decode(self.request.get("email"))
        subscribe = decode(self.request.get("subscribe"))
        target_url = decode(self.request.get('continue'))
        target_url = target_url or self.uri_for('account')

        # Set a flag whether newsletter subscription setting has changed
        subscription_changed = bool(self.userprefs.subscribed_to_newsletter) \
                is not bool(subscribe)

        # Update UserPrefs object
        self.userprefs.is_setup = True
        self.userprefs.nickname = username
        self.userprefs.email = email
        self.userprefs.email_md5 = md5(email.strip().lower()).hexdigest()
        self.userprefs.subscribed_to_newsletter = bool(subscribe)
        self.userprefs.put()

        # Subscribe this user to the email newsletter now (if wanted). By
        # default does not subscribe users to mailchimp in Test Environment!
        if subscription_changed and webapp2.get_app().config.get('mailchimp')['enabled']:
            if subscribe:
                tools.mailchimp.mailchimp_subscribe(email)
            else:
                tools.mailchimp.mailchimp_unsubscribe(email)

        # After updating UserPrefs, redirect
        self.redirect(target_url)

class NotFound(BaseRequestHandler):
    def get(self):
        self.error404()
        
    def post(self):
        self.error404()