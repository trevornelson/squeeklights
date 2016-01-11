from models import Content

def homepage():
	hero_text = "More Than Just Being Seen"
	if Content.all().count() == 0:
		c = Content(hero_text=hero_text)
		c.put()