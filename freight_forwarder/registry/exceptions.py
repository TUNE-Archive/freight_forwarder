# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import json


# TODO: update with more specific exceptions
class RegistryException(Exception):
    def __init__(self, response):
        self.response = response

        if hasattr(response, 'content'):
            try:
                data = json.loads(response.content)
                self.message = data['error'] if 'error' in data else "An unknown exception was found."
            except:
                self.message = "Unable to contact registry at '{0}'.  Status {1}.".format(response.request.url, response.status_code)

        else:
            self.message = "There was an issue with the request to the docker registry."

        super(RegistryException, self).__init__(self.message)

    def __str__(self):
        return super(RegistryException, self).__str__()
