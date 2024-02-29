from django.conf import settings


def settings_processor(request):
    return {"app_name": settings.APP_NAME}
