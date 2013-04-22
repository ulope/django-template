from importlib import import_module
import socket
import traceback
from django.core.exceptions import ImproperlyConfigured
import sys
from logging import getLogger

log = getLogger(__name__)


class ConfigurationManager(object):
    settings_package = None
    hostmap = None

    def __init__(self):
        if not self.settings_package or not self.hostmap:
            raise ImproperlyConfigured(
                "You need to define 'settings_module' and 'hostmap' in your "
                "ConfigurationManager subclass.")

    def configure(self):
        # This only works if the subclass is actually defined in the target module!
        target_module = sys.modules[self.__class__.__module__]

        base_settings = import_module("{0}.settings".format(self.settings_package))

        # start by copying all settings from the base settings module
        self._update_module_globals(base_settings, target_module)

        to_load = set()
        # use both getfqdn() and gethostname() since getfqdn() alone might not
        # return something usefull (e.g. with no network interfaces)
        hostnames = (socket.getfqdn(), socket.gethostname())
        for hostname in hostnames:
            for configuration_name, hostname_candiates in self.hostmap.items():
                if hostname in hostname_candiates:
                    to_load.add(configuration_name)

        if not to_load:
            raise ImproperlyConfigured("No host-specific config found. Make sure there is a configuration for your hostname(s) {0}.".format(', '.join(hostnames)))

        for configuraion_name in to_load:
            settings_path = '{0}.settings_{1}'.format(self.settings_package, configuraion_name)
            try:
                configuration_module = import_module(settings_path)
                self._update_module_globals(configuration_module, target_module, merge=True)
            except SyntaxError as exc:
                raise ImproperlyConfigured(
                    "Host specific settings module '{0}' could not be imported because it contains syntax errors:\n{1.filename} (L{1.lineno}): {1.text}".format(
                        settings_path, exc
                    ))
            except ImportError:
                raise ImproperlyConfigured("Host specific settings module '{0}' could not be imported.\n{1}".format(
                    settings_path, traceback.format_exception(*sys.exc_info())
                ))



    def _update_module_globals(self, source, target, merge=False):
        for attr in dir(source):
            if attr.upper() == attr:
                source_value = getattr(source, attr)
                if merge:
                    if hasattr(target, attr):
                        target_value = getattr(target, attr)
                        if (isinstance(source_value, (list, tuple,))
                            and isinstance(target_value, (list, tuple,))):
                            setattr(target, attr, target_value + source_value)
                            continue
                        elif (isinstance(source_value, dict)
                              and isinstance(target_value, dict)):
                            setattr(target, attr, self._merge_dict(target_value, source_value))
                            continue

                # Fall trough
                setattr(target, attr, source_value)

    @staticmethod
    def _merge_dict(dst, src):
        stack = [(dst, src)]
        while stack:
            current_dst, current_src = stack.pop()
            for key in current_src:
                if key not in current_dst:
                    current_dst[key] = current_src[key]
                else:
                    if isinstance(current_src[key], dict) and isinstance(current_dst[key], dict):
                        stack.append((current_dst[key], current_src[key]))
                    else:
                        current_dst[key] = current_src[key]
        return dst

