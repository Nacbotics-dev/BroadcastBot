from django.contrib import admin
from .models import Channel,STEP

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    search_fields = ['ChannelId','chat_id','chat_name','chat_admin',]
    list_display = ['ChannelId','chat_id','chat_name','chat_admin','date_added',]

    class Meta:
        verbose_name_plural = "Channels"

@admin.register(STEP)
class STEPAdmin(admin.ModelAdmin):
    search_fields = ['step_id','user',]
    list_display = ['step_id','user','next_step','state',]

    class Meta:
        verbose_name_plural = "Steps"

