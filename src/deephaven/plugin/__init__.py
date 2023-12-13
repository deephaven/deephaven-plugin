import abc
from typing import Union, Type

"""
The deephaven.plugin module provides an API and registration mechanism to add new behavior to the Deephaven
server. Plugins should be registered by adding a Registration instance as an entrypoint to the Python package.
"""
__version__ = "0.6.0"

DEEPHAVEN_PLUGIN_ENTRY_KEY = "deephaven.plugin"
DEEPHAVEN_PLUGIN_REGISTRATION_CLASS = "registration_cls"


class Plugin(abc.ABC):
    pass


class Callback(abc.ABC):
    """
    An instance of Callback will be passed to Registration.register_into, to allow any number of plugins to be
    registered.
    """

    @abc.abstractmethod
    def register(self, plugin: Union[Plugin, Type[Plugin]]) -> None:
        """
        Registers a given plugin type for use in the Deephaven server. Should be called from from a Registration's
        register_into method, so that it is available when the server expects it.
        :param plugin: the plugin or plugin type to register on the server
        :return:
        """
        pass


class Registration(abc.ABC):
    """
    Registration types should be set as the registration_cls for deephaven.plugin entrypoints for their package to
    ensure that they are all run on server startup.
    """

    @classmethod
    @abc.abstractmethod
    def register_into(cls, callback: Callback) -> None:
        """
        Implement this method and reference this Registration type from the package's entrypoint to ensure that any
        provided plugins are available at server startup. Invoke callback.register() once for each provided plugin.
        :param callback: invoke this once per plugin to register them for use in the server.
        :return:
        """
        pass

    @classmethod
    def collect_plugins(cls):
        class Collector(Callback):
            def __init__(self) -> None:
                self._output = []

            def register(self, plugin: Union[Plugin, Type[Plugin]]) -> None:
                self._output.append(plugin)

        collector = Collector()
        cls.register_into(collector)
        return collector._output


def collect_registration_entrypoints():
    import sys

    if sys.version_info < (3, 8):
        from importlib_metadata import entry_points
    elif sys.version_info < (3, 10):
        from importlib.metadata import entry_points as ep

        def entry_points(group, name):
            # Looks to be a bug in 3.8, 3.9 where entries are doubled up
            entries = set(ep()[group] or [])
            return [e for e in entries if e.name == name]

    else:
        from importlib.metadata import entry_points
    return (
        entry_points(
            group=DEEPHAVEN_PLUGIN_ENTRY_KEY, name=DEEPHAVEN_PLUGIN_REGISTRATION_CLASS
        )
        or []
    )


def collect_registration_classes():
    return [e.load() for e in collect_registration_entrypoints()]


def register_all_into(callback: Callback):
    for registration_cls in collect_registration_classes():
        registration_cls.register_into(callback)


def list_registrations():
    output = "Listing Deephaven Plugin registrations:"
    for registration_cls in collect_registration_classes():
        output += f"\n  {registration_cls}"
    print(output)


def list_plugins():
    output = "Listing Deephaven Plugins:"
    for registration_cls in collect_registration_classes():
        output += f"\n  {registration_cls}"
        plugins = registration_cls.collect_plugins()
        output += "".join([f"\n    {plugin}" for plugin in plugins])
    print(output)


def list_registrations_console():
    """
    Entrypoint for the console script deephaven-plugin-list-registrations
    """
    list_registrations()


def list_plugins_console():
    """
    Entrypoint for the console script deephaven-plugin-list-plugins
    """
    list_plugins()
