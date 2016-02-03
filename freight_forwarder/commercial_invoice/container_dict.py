# -*- coding: utf-8; -*-
from __future__ import unicode_literals

try:
    from UserDict    import UserDict
except ImportError:
    from collections import UserDict

from docker import errors

from freight_forwarder.container import Container


class ContainerDict(UserDict):
    def __init__(self):
        UserDict.__init__(self)
        self._first = None

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __delitem__(self, key):
        if key in self.data:
            try:
                if self.data[key].state()['running']:
                    self.data[key].stop()

                # TODO: allow user to specify if they want to remove volumes
                self.data[key].delete(remove_volumes=True)

            except errors.APIError as e:
                if e.response.status_code is 404:
                    pass

            del self.data[key]
        else:
            # TODO: maybe error out maybe not?
            pass

    def __setitem__(self, key, value):
        if not isinstance(value, Container):
            raise Exception("ContainerDict only take instances of Container.")

        if self._first is None:
            self._first = value

        self.data[key] = value

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]

        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)

        raise KeyError(key)

    @property
    def first(self):
        return self._first
