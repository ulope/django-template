from configuration_management import ConfigurationManager


class Settings(ConfigurationManager):
    settings_package = "{{ project_name }}.project_settings"
    hostmap = {
        'dev': (
        ),
        'live': (
        )
    }


Settings().configure()
