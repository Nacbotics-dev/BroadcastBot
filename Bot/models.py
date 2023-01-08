from uuid import uuid4
from django.db import models



class Channel(models.Model):
    ChannelId = models.UUIDField(blank=False,default=uuid4,primary_key=True,editable=False)
    chat_id = models.CharField(blank=False,max_length=50,unique=True) #this is the channel/group id
    chat_name = models.CharField(blank=False,max_length=100,default='my Channell') #This is the name of the channel/group
    chat_admin = models.CharField(blank=False,max_length=100) #This is the id of the user that added the bot
    date_added = models.DateTimeField(auto_now_add=True)


class STEP(models.Model):
	"""
	Model re-presenting a user'r client
	"""

	step_id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
	user = models.CharField(blank=False,max_length=50,unique=True)
	next_step = models.CharField(max_length=20,default='')# The current step the use is in
	state = models.TextField(blank = True,null=True)

	def __str__(self):
		return(str(self.step_id))