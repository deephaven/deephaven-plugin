import abc
import json
import pathlib
import typing

from . import Plugin


class JsType(Plugin):
    """A javascript type plugin. Useful for adding custom javascript code to the server."""

    @abc.abstractmethod
    def path(self) -> typing.Generator[pathlib.Path, None, None]:
        """A generator that yields the path to package.json."""
        pass

    def package_dict(self) -> dict:
        """Returns package.json as a dict"""
        with self.path() as path:
            with open(path) as file:
                return json.load(file) 

    @property
    def name(self) -> str:
        """Returns the name field from package.json"""
        return self.package_dict()['name']

    @property
    def version(self) -> str:
        """Returns the version field from package.json"""
        return self.package_dict()['version']

    def __str__(self) -> str:
        pd = self.package_dict()
        name = pd['name']
        version = pd['version']
        return f"{name}@{version}"
