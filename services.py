# -*- coding: utf-8 -*-
import os
# from google.appengine.dist import use_library
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
use_library('django', '1.2')

"""
Services that are accessible to admin only (eg. cron).
"""

from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models import *
from handlers import *
import instagram
import time


class Cron1(webapp.RequestHandler):
    def get(self):
        """Cron job that queries the db and forks a worker for each entry"""
        emails = db.GqlQuery("SELECT * FROM emails WHERE 1")

        # Start worker requests in the background
        for email in emails:
            taskqueue.add(url='/services/cron1-worker1/%s' % email.key())


class Cron1_Worker1(webapp.RequestHandler):
    def post(self, key):
        """Worker that runs in the 'background'"""
        # Get the object from the database
        email = Emails.get(key)

        # Construct a appengine.api.mail object
        message = mail.EmailMessage()
        message.sender = "Your Name <you@domain.x>"
        message.to = email.to
        message.subject = email.subject

        # Set text and html body
        message.body = email.body_text
        message.html = email.body_html

        # Send. Important: Sometimes emails fail to send, which will throw an
        # exception and end the function there. Next round tries again.
        message.send()

        # Now the message was sent and we can safely delete it.
        email.delete()

class fetchInstagram(webapp.RequestHandler):
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
                show.images = image_urls
                show.put()




urls = [
    (r'/services/cron1', Cron1),
    (r'/services/cron1-worker1', Cron1_Worker1),
    (r'/services/fetch-instagram', fetchInstagram)
]

application = webapp.WSGIApplication(urls, debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
