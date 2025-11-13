from django.conf import settings

def global_settings(request):
    return {
        'external_shop_url': getattr(settings, 'EXTERNAL_SHOP_URL', ''),
        'facebook_page_url': getattr(settings, 'SOCIAL_FACEBOOK_URL', 'https://www.facebook.com/natursur'),
        'youtube_channel_url': getattr(settings, 'YOUTUBE_CHANNEL_ID', ''),
    }
