from django.apps import AppConfig


class SocialsConfig(AppConfig):
    name = 'socials'

    def ready(self):
        try:
            import socials.recievers
        except ImportError:
            pass
