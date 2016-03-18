# -*- coding: utf-8; -*-k
from __future__ import unicode_literals
import re
import os
import json
from collections import OrderedDict
from difflib     import get_close_matches

import six
from yaml             import SafeLoader, YAMLError
from yaml.constructor import SafeConstructor

from .utils import logger, normalize_keys, normalize_value


ACTIONS_SCHEME = {
    'deploy': {'inherit': '$action'},
    'offload': {'inherit': '$action'},
    'test': {'inherit': '$action'},
    'export': {'inherit': '$action'},
    'quality_control': {'inherit': '$action'}
}

ENVIRONMENTS_SCHEME = {
    'is': {
        'type': dict,
        'one_of': (
            'ci',
            'dev',
            'development',
            'test',
            'testing',
            'perf',
            'performance',
            'stage',
            'staging',
            'beta',
            'integration',
            'prod',
            'production'
        )
    },
    'dev': {'inherit': '$environment'},
    'development': {'inherit': '$environment'},
    'ci': {'inherit': '$environment'},
    'test': {'inherit': '$environment'},
    'testing': {'inherit': '$environment'},
    'perf': {'inherit': '$environment'},
    'performance': {'inherit': '$environment'},
    'stage': {'inherit': '$environment'},
    'staging': {'inherit': '$environment'},
    'beta': {'inherit': '$environment'},
    'integration': {'inherit': '$environment'},
    'prod': {'inherit': '$environment'},
    'production': {'inherit': '$environment'},
    '@services': {},

    '*': {
        'ref': 'hosts',
        'is': {
            'one_of': [
                {
                    'is': {
                        'type': list,
                        'items': {
                            'inherit': '$host'
                        }
                    }
                },
                {'inherit': '$host'}
            ]

        }
    }
}
REGISTRIES_SCHEME = {
    'is': {
        'type': dict,
    },
    '*': {
        'ref': 'registries',
        'inherit': '$host',
        'auth': {
            'inherit': '$host',
            'is': {
                'type': dict,
                'required': ['type']
            },
            'type': {
                'is': {
                    'one_of': ('basic', 'registry_rubber'),
                    'type': six.string_types,
                }
            }
        },
        'verify': {
            'is': {
                'type': bool
            }
        }
    }
}

ROOT_SCHEME = {
    'is': {
        'required': [
            'environments',
            'project',
            'team',
            'repository'
        ]
    },
    'environments': ENVIRONMENTS_SCHEME,
    'project': {
        'is': {
            'type': six.string_types,
        }
    },
    'team': {
        'is': {
            'type': six.string_types,
        }
    },
    'registries': REGISTRIES_SCHEME,
    'repository': {
        'is': {
            'type': six.string_types,
        }
    },
    '*': {
        'ref': 'services',
        'inherit': '$service',
        'is': {
            'type': dict,
            'one_of': ('image', 'build')
            # 'min': 1
        }
    },
    '_': {
        'action': {
            'ref': 'actions',
            'is': {
                'type': dict,
                'one_of': '~services'
            },
            '@services': {}
        },
        'service': {
            'is': {
                'type': dict,
                'one_of': ('image', 'build')
            },
            'cascading': True,
            'attach_stderr': {
                'is': {
                    'type': bool
                }
            },
            'attach_stdin': {
                'is': {
                    'type': bool
                }
            },
            'attach_stdout': {
                'is': {
                    'type': bool
                }
            },
            'build': {
                'is': {
                    'type': six.string_types
                }
            },
            'binds': {
                'is': {
                    'type': list
                }
            },
            'cap_add': {
                'is': {
                    'type': list,
                    'items': {
                        'is': {
                            'type': six.string_types
                        }
                    }
                }
            },
            'cap_drop': {
                'is': {
                    'type': list,
                    'items': {
                        'is': {
                            'type': six.string_types
                        }
                    }
                }
            },
            'cgroup_parent': {
                'is': {
                    'type': six.string_types
                }
            },
            'command': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': six.string_types,
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                }
            },
            'cmd': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': six.string_types,
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                }
            },
            'cpu_shares': {
                'is': {
                    'type': int
                }
            },
            'devices': {
                'is': {
                    'type': list
                }
            },
            'domain_name': {
                'is': {
                    'type': six.string_types
                }
            },
            'domainname': {
                'is': {
                    'type': six.string_types
                }
            },
            'detach': {
                'is': {
                    'type': bool
                }
            },
            'dns': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': six.string_types,
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                }
            },
            'dns_search': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': six.string_types,
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                }
            },
            'entrypoint': {
                # TODO: add one_of
                'is': {
                    'type': (list, six.string_types)
                }
            },
            'entry_point': {
                # TODO: add one of
                'is': {
                    'type': (list, six.string_types)
                }
            },
            'env': {
                'is': {
                    'type': list,
                    'items': {
                        'is': {
                            'type': six.string_types
                        }
                    }
                }
            },
            'env_vars': {
                'is': {
                    'type': list,
                    'items': {
                        'is': {
                            'type': six.string_types
                        }
                    }
                }
            },
            'export_to': {
                'is': {
                    'one_of': '~registries',
                    'type': six.string_types
                }
            },
            'exposed_ports': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': dict,
                            },
                            '*': {
                                'is': {
                                    'type': six.string_types
                                }
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                },
                '*': {
                    'is': {
                        'type': six.string_types
                    }
                }
            },
            'extra_hosts': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': dict,
                            },
                            '*': {
                                'is': {
                                    'type': six.string_types
                                }
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                },
                '*': {
                    'is': {
                        'type': six.string_types
                    }
                }
            },
            'hostname': {
                'is': {
                    'type': six.string_types
                }
            },
            'image': {
                'is': {
                    'type': six.string_types,
                }
            },
            'links': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': dict,
                            },
                            '*': {
                                'is': {
                                    'type': six.string_types
                                }
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                },
                '*': {
                    'is': {
                        'type': six.string_types
                    }
                }
            },
            'labels': {
                'is': {
                    'type': dict
                }
            },
            'log_config': {
                'is': {
                    'type': dict,
                    'required': ['type', 'config']
                },
                'type': {
                    'is': {
                        'type': six.string_types
                    }
                },
                'config': {
                    'is': {
                        'required': ['syslog-facility'],
                        'type': dict
                    },
                    'syslog-facility': {
                        'is': {
                            'type': six.string_types
                        }
                    },
                    'syslog-tag': {
                        'is': {
                            'type': six.string_types
                        }
                    }
                }
            },
            'lxc_conf': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': dict,
                            },
                            '*': {
                                'is': {
                                    'type': six.string_types
                                }
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                },
                '*': {
                    'is': {
                        'type': six.string_types
                    }
                }
            },
            'memory': {
                'is': {
                    'type': int
                }
            },
            'memory_swap': {
                'is': {
                    'type': int
                }
            },
            'network_disabled': {
                'is': {
                    'type': bool
                }
            },
            'network_mode': {
                'is': {
                    'type': six.string_types,
                }
            },
            'open_stdin': {
                'is': {
                    'type': bool
                }
            },
            'ports': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': dict,
                            },
                            '*': {
                                'is': {
                                    'type': list
                                }
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                },
                '*': {
                    'is': {
                        'type': list
                    }
                }
            },
            'ports_bindings': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': dict,
                            },
                            '*': {
                                'is': {
                                    'type': list
                                }
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                },
                '*': {
                    'is': {
                        'type': list
                    }
                }
            },
            'privileged': {
                'is': {
                    'type': bool
                }
            },
            'publish_all_ports': {
                'is': {
                    'type': bool
                }
            },
            'readonly_root_fs': {
                'is': {
                    'type': bool
                }
            },
            'readonly_rootfs': {
                'is': {
                    'type': bool
                }
            },
            'restart': {
                'is': {
                    'type': dict
                }
            },
            'security_opt': {
                'is': {
                    'type': list
                }
            },
            'stdin_once': {
                'is': {
                    'type': bool
                }
            },
            'tags': {
                'is': {
                    'type': list,
                    'items': {
                        'is': {
                            'type': six.string_types
                        }
                    }
                }
            },
            'test': {
                'is': {
                    'type': six.string_types,
                }
            },
            'tty': {
                'is': {
                    'type': bool
                }
            },
            'ulimits': {
                'is': {
                    'type': list
                }

            },
            'user': {
                'is': {
                    'type': six.string_types
                }
            },
            'volumes': {
                'is': {
                    'one_of': [
                        {
                            'is': {
                                'type': dict,
                            },
                            '*': {
                                'is': {
                                    'type': six.string_types
                                }
                            }
                        },
                        {
                            'is': {
                                'type': list,
                                'items': {
                                    'is': {
                                        'type': six.string_types
                                    }
                                }
                            },
                        }

                    ]
                },
                '*': {
                    'is': {
                        'type': six.string_types
                    }
                }
            },
            'volumes_from': {
                'is': {
                    'type': (list, six.string_types)
                }
            },
            'working_dir': {
                'is': {
                    'type': six.string_types
                }
            }
        },
        'environment': {
            'ref': 'environments',
            'is': {
                'type': dict,
            },
            '@services': {},
            'hosts': {
                'is': {
                    'type': dict,
                },
                'default': {
                    'is': {
                        'type': list,
                        'items': {
                            'inherit': '$host'
                        }
                    }
                },
                'export': {
                    'is': {
                        'type': list,
                        'items': {
                            'inherit': '$host'
                        },
                        'max': 1
                    }
                },
                '~services': {
                    'is': {
                        'type': list,
                        'items': {
                            'inherit': '$host'
                        }
                    }
                }
            },
            '*': {
                'ref': 'data_centers',
                'inherit': '$data_center'
            }
        },

        # TODO: make object more bullet proof
        'data_center': {
            'inherit': '$actions',
            'is': {
                'type': dict,
            },
            '@services': {},
            'hosts': {
                'cascading': True,
                'is': {
                    'type': dict
                },
                'default': {
                    'is': {
                        'type': list,
                        'items': {
                            'inherit': '$host'
                        }
                    }
                },
                'export': {
                    'is': {
                        'type': list,
                        'items': {
                            'inherit': '$host'
                        },
                        'max': 1
                    }
                },
                '~services': {
                    'is': {
                        'type': list,
                        'items': {
                            'inherit': '$host'
                        }
                    }
                }
            }
        },

        'actions': ACTIONS_SCHEME,

        'host': {
            'is': {
                'type': dict,
                'required': ['address']
            },
            'address': {
                'is': {
                    'type': six.string_types
                }
            },
            'ssl_cert_path': {
                'is': {
                    'type': six.string_types
                }
            },
            'verify': {
                'is': {
                    'type': bool
                }
            }

        }
    }
}

VALIDATORS = (
    'required',
    'must_include',
    'type',
    'one_of',
    'if',
    'any_of',
    'items',
    'not',
    'max',
    'min',
)

RESERVED_SCHEME_KEYS = (
    'is',
    'ref',
    'inherit',
    'cascading',
    '_',
    '*',
    '~',
    '$',
    '@',
)

extract_doc_string = re.compile(
    r'''^ (@|)     # explicit module name
          (\w+):   # thing name
          \s?(.*)$ # rest should be comma seperated values.
          ''', re.VERBOSE)


class Config(object):
    """ A representation of a freight-forwarder configuration file.

    :param verbose: A :boolean:, will provide verbose validation output. defaults to True
    * not yet implemented.
    :param path_override: A :string:, a path to a configuration to override. defaults to cwd
    """
    def __init__(self, path_override=None, verbose=True):
        self._scheme_references = {}
        self._data              = None

        if path_override and not isinstance(path_override, six.string_types):
            raise TypeError(logger.error("path_override must be a string."))

        self._path    = path_override if path_override else os.getcwd()
        self._verbose = verbose

        self._load()

    def get(self, attr_name, *args):
        """ Get the most retrieval attribute in the configuration file.  This method
        will recursively look through the configuration file for the attribute specified
        and return the last found value or None. The values can be referenced by
        the key name provided in the configuration file or that value normalized with
        snake_casing.

        Usage::
            >>> from freight_forwarder.config import Config
            >>>
            >>> config = Config()
            >>> thing = config.get('thing', 'grandparent', 'parent')

        :param attr_name: A :string: The configuration property name to get.
        :param *args: A :tuple: if :strings: parent objects in which to look for attr. This is optional.
        :return attr value:
        """
        if not isinstance(attr_name, six.string_types):
            raise TypeError('attr_name must be a str.')

        # allow retrieval of data with alias or normalized name
        if '-' in attr_name:
            attr_name = attr_name.replace('-', '_')

        parent_attr = self
        attr = getattr(parent_attr, attr_name, None)

        for arg in args:
            if not isinstance(arg, six.string_types):
                raise TypeError(
                    'each additional argument must be a string. {0} was not a string'.format(arg)
                )

            if hasattr(parent_attr, arg):
                parent_attr = getattr(parent_attr, arg)

                if hasattr(parent_attr, attr_name):
                    attr = getattr(parent_attr, attr_name)
        else:
            pass

        return attr

    # TODO: revisit these reference functions to validate there usefulness.
    @property
    def service_references(self):
        """ returns a list of service names
        """
        services_blue_print = self._scheme_references.get('services')
        if services_blue_print is None:
            raise LookupError('unable to find any services in the config.')

        # TODO: this needs to be cleaned up and made solid. maybe when creating the blueprint ref normalize the damn keys
        return {key.replace('-', '_'): key for key in services_blue_print['keys']}

    def environment_references(self):
        services_blue_print = self._scheme_references.get('environments')
        if services_blue_print is None:
            raise LookupError('unable to find any environments in the config.')

        # TODO: this needs to be cleaned up and made solid. maybe when creating the blueprint ref normalize the damn keys
        return {key.replace('-', '_'): key for key in services_blue_print['keys']}

    def data_center_references(self, environment):
        """

        :param string environment:
        :return dict:
        """
        services_blue_print = self._scheme_references.get('data_centers')
        if services_blue_print is None:
            raise LookupError('unable to find any data_centers in the config.')

        if environment not in self.environments:
            raise LookupError('unable to find {0} in the following environments: {1}'.format(
                environment, ', '.join(self.environment_references().keys())
            ))

        environment = self.environments[environment]
        # TODO: this needs to be cleaned up and made solid. maybe when creating the blueprint ref normalize the damn keys
        return {key.replace('-', '_'): key for key in services_blue_print['keys'] if key.replace('-', '_') in environment}

    def validate(self):
        """ Validate the contents of the configuration file. Will return None if validation is successful or
        raise an error if not.
        """
        if not isinstance(self._data, dict):
            raise TypeError('freight forwarder configuration file must be a dict.')

        current_log_level = logger.get_level()

        if self._verbose:
            logger.set_level('DEBUG')
        else:
            logger.set_level('ERROR')

        logger.info('Starting configuration validation', extra={"formatter": 'config-start'})

        # copy config dict to allow config data to stay in its original state.
        config_data = self._data.copy()

        try:
            self._walk_tree(config_data, ROOT_SCHEME)
        except ConfigValidationException as e:
            e.log_error()
            raise

        logger.info("Config validation passed.", extra={'formatter': 'config-success'})

        logger.set_level(current_log_level)

    ##
    # private methods
    ##
    def _load(self):
        """ Load a configuration file.  This method will be called when the Config class is instantiated.  The
        configuration file can be json or yaml.
        """
        if os.path.isdir(self._path):
            for file_ext in ('yml', 'yaml', 'json'):
                test_path = os.path.join(self._path, 'freight-forwarder.{0}'.format(file_ext))

                if os.path.isfile(test_path):
                    self._path = test_path
                    break

        if os.path.isfile(self._path):
            file_name, file_extension = os.path.splitext(self._path)

            with open(self._path, 'r') as config_file:
                if file_extension in ('.yaml', '.yml'):
                    self._load_yml_config(config_file.read())
                elif file_extension == '.json':
                    try:
                        config_data = json.loads(config_file.read())
                        self._data  = normalize_keys(config_data)
                    except Exception:
                        raise SyntaxError("There is a syntax error in your freight-forwarder config.")
                else:
                    raise TypeError("Configuration file most be yaml or json.")
        else:
            raise LookupError("Was unable to find a freight-forwarder configuration file.")

    def _load_yml_config(self, config_file):
        """ loads a yaml str, creates a few constructs for pyaml, serializes and normalized the config data. Then
         assigns the config data to self._data.

        :param config_file: A :string: loaded from a yaml file.
        """
        if not isinstance(config_file, six.string_types):
            raise TypeError('config_file must be a str.')

        try:
            def construct_yaml_int(self, node):
                obj  = SafeConstructor.construct_yaml_int(self, node)
                data = ConfigInt(
                    obj,
                    node.start_mark,
                    node.end_mark
                )

                return data

            def construct_yaml_float(self, node):
                obj, = SafeConstructor.construct_yaml_float(self, node)
                data = ConfigFloat(
                    obj,
                    node.start_mark,
                    node.end_mark
                )

                return data

            def construct_yaml_str(self, node):
                # Override the default string handling function
                # to always return unicode objects
                obj = SafeConstructor.construct_scalar(self, node)

                assert isinstance(obj, six.string_types)
                data = ConfigUnicode(
                    obj,
                    node.start_mark,
                    node.end_mark
                )

                return data

            def construct_yaml_mapping(self, node):
                obj, = SafeConstructor.construct_yaml_map(self, node)
                data = ConfigDict(
                    obj,
                    node.start_mark,
                    node.end_mark
                )

                return data

            def construct_yaml_seq(self, node):
                obj, = SafeConstructor.construct_yaml_seq(self, node)
                data = ConfigSeq(
                    obj,
                    node.start_mark,
                    node.end_mark
                )

                return data

            # SafeConstructor.add_constructor(u'tag:yaml.org,2002:bool',  construct_yaml_bool)
            SafeConstructor.add_constructor(u'tag:yaml.org,2002:float', construct_yaml_float)
            SafeConstructor.add_constructor(u'tag:yaml.org,2002:int', construct_yaml_int)
            SafeConstructor.add_constructor(u'tag:yaml.org,2002:map', construct_yaml_mapping)
            SafeConstructor.add_constructor(u'tag:yaml.org,2002:seq', construct_yaml_seq)
            SafeConstructor.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)

            data = SafeLoader(config_file).get_data()
            if data is None:
                raise AttributeError('The configuration file needs to have data in it.')

            self._data = normalize_keys(data, snake_case=False)
        except YAMLError as e:
            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                raise SyntaxError(
                    "There is a syntax error in your freight-forwarder config file line: {0} column: {1}".format(
                        mark.line + 1,
                        mark.column + 1
                    )
                )
            else:
                raise SyntaxError("There is a syntax error in your freight-forwarder config.")

    def _merge_config(self, config_override):
        """ overrides and/or adds data to the current configuration file.

        ** This has not been implemented yet.

        :param config_override: A :string: config data to add to or override the current config.
        """
        if not isinstance(config_override, dict):
            raise TypeError("config override must be a dict")

        def recursion(config_value, override_value):
            for key, value in override_value.items():
                if key in config_value:
                    if isinstance(value, dict) and isinstance(config_value[key], dict):
                        recursion(config_value[key], value)
                    else:
                        config_value[key] = value
                else:
                    config_value[key] = value

        for key, value in config_override.items():
            if key in self._data:
                recursion(self._data[key], value)
            else:
                self._data[key] = value

    def _create_attr(self, property_key, data, ancestors):
        """ Dynamically Creates attributes on for a Config.  Also adds name and alias to each Config object.

        :param property_key: A :string: configuration property name.
        :param data: The adds the user supplied for this specific property.
        :param ancestors: A :OrderedDict: that provides a history of its ancestors.
        """
        if not isinstance(property_key, six.string_types):
            raise TypeError("property_key must be a string. type: {0} was passed.".format(type(property_key)))

        if not isinstance(ancestors, OrderedDict):
            raise TypeError("ancestors must be an OrderedDict. type: {0} was passed.".format(type(ancestors)))

        previous_element        = self
        normalized_key          = normalize_value(property_key).replace('-', '_')
        normalized_ancestor_key = None

        # TODO: clean up and validation
        if ancestors:
            for ancestor_key, ancestors_value in six.iteritems(ancestors):
                normalized_ancestor_key = normalize_value(ancestor_key).replace('-', '_')

                if normalized_ancestor_key.lower() == 'root':
                    continue

                if not hasattr(previous_element, normalized_ancestor_key):
                    config_attr       = ConfigDict({}, ancestors_value.start_mark, ancestors_value.end_mark)
                    config_attr.name  = normalized_ancestor_key
                    config_attr.alias = ancestor_key

                    setattr(
                        previous_element,
                        normalized_ancestor_key,
                        config_attr
                    )

                previous_element = getattr(previous_element, normalized_ancestor_key)

        if normalized_key == normalized_ancestor_key:
            pass
        else:
            if isinstance(data, ConfigNode):
                data.name  = normalized_key
                data.alias = property_key

            setattr(previous_element, normalized_key, data)

    def _collect_unrecognized_values(self, scheme, data, ancestors):
        """ Looks for values that aren't defined in the scheme and returns a dict with any unrecognized values found.

        :param scheme: A :dict:, The scheme defining the validations.
        :param data: A :dict: user supplied for this specific property.
        :param ancestors: A :OrderedDict: that provides a history of its ancestors.
        :rtype: A :dict: of unrecognized configuration properties.
        """
        if not isinstance(ancestors, OrderedDict):
            raise TypeError("ancestors must be an OrderedDict. type: {0} was passed.".format(type(ancestors)))

        if not isinstance(scheme, dict):
            raise TypeError('scheme must be a dict. type: {0} was passed'.format(type(scheme)))

        unrecognized_values = {}
        if isinstance(data, dict):
            pruned_scheme = [key for key in scheme.keys() if key not in RESERVED_SCHEME_KEYS and key[0] not in RESERVED_SCHEME_KEYS]

            for key, value in six.iteritems(data):
                if key in pruned_scheme:
                    continue

                unrecognized_values[key] = value

            validations = scheme.get('is')
            if validations and 'one_of' in validations:
                for nested_scheme in validations['one_of']:
                    if isinstance(nested_scheme, dict):

                        updated_scheme = self._update_scheme(nested_scheme, ancestors)
                        pruned_scheme = [key for key in updated_scheme.keys() if key not in RESERVED_SCHEME_KEYS and key[0] not in RESERVED_SCHEME_KEYS]
                        for key in pruned_scheme:
                            if key in unrecognized_values:
                                del unrecognized_values[key]
        else:
            # TODO: maybe return an error?
            pass

        return unrecognized_values

    def _update_scheme(self, scheme, ancestors):
        """ Updates the current scheme based off special pre-defined keys and retruns a new updated scheme.

        :param scheme: A :dict:, The scheme defining the validations.
        :param ancestors: A :OrderedDict: that provides a history of its ancestors.
        :rtype: A new :dict: with updated scheme values.
        """
        if not isinstance(ancestors, OrderedDict):
            raise TypeError("ancestors must be an OrderedDict. type: {0} was passed.".format(type(ancestors)))

        if not isinstance(scheme, dict):
            raise TypeError('scheme must be a dict. type: {0} was passed'.format(type(scheme)))

        # TODO: what if we have more than one scheme :P need to fix this.
        definitions = ROOT_SCHEME.get('_')
        if 'inherit' in scheme:
            scheme = self._scheme_propagation(scheme, definitions)

        updated_scheme = {}
        for scheme_key in six.iterkeys(scheme):
            if not isinstance(scheme_key, six.string_types):
                raise TypeError('scheme keys are required to be strings. type: {0} was passed.'.format(scheme_key))

            if '@' in scheme_key:
                ref = scheme_key[1:]

                scheme_reference = self._scheme_references.get(ref)
                if not scheme_reference:
                    raise ConfigValidationException(ancestors, ref, scheme_reference, 'required', scheme)

                for reference_key in scheme_reference['keys']:
                    scheme_reference['scheme'].update(scheme[scheme_key])
                    updated_scheme[reference_key] = scheme_reference['scheme']

            elif '~' in scheme_key:
                ref = scheme_key[1:]

                scheme_reference = self._scheme_references.get(ref)
                if not scheme_reference:
                    raise LookupError("was unable to find {0} in scheme reference.".format(ref))

                for reference_key in scheme_reference['keys']:
                    updated_scheme[reference_key] = scheme[scheme_key]

        scheme.update(updated_scheme)
        return scheme

    def _get_cascading_attr(self, attr_name, *args):
        """ Will traverse the configuration data looking for attr_name provided.  It will know where to look for the
        attribute based on the *args that are passed to the method.  It treats the args as ancestors starting with the
        oldest `root -> grandparent -> parent -> attr_name`.  The findings will be updated with the last found object.
        The properties in the last found object will overwrite those in the previous.  If the attribute isn't found
        will return None

        Usage::
            >>> attr = self._get_cascading_attr('attribute_name', 'root', 'grandparent', 'parent')
            >>> if attr is not None:
            >>>  do_thing(attr)

        :param attr_name: A string, the configuration attribute name
        :param *args: A list, A list of strings that that represent the attributes ancestry. (how to find the obj)
        :rtype: Any defined configuration value :dict:, :string:, :int:, :list:, :float: `attr`
        """
        attr = self._data.get(attr_name, None)
        if isinstance(attr, ConfigDict):
            attr = ConfigDict(attr, attr.start_mark, attr.end_mark)
        elif isinstance(attr, dict):
            attr = attr.copy()

        cascading = self._data
        if args:

            for key in args:
                if not isinstance(key, six.string_types):
                    raise TypeError('Every key in args must be a string.')

                if key in cascading:
                    config_object = cascading.get(key)

                    if config_object:
                        if attr_name in config_object:
                            if isinstance(attr, dict):
                                value = config_object[attr_name]

                                if value is None:
                                    attr = value
                                elif isinstance(value, dict):
                                    attr.update(config_object[attr_name])
                                else:
                                    raise LookupError(
                                        "Unable to find '{0}'. Obj structure: {1}".format(
                                            attr_name, " -> ".join(args)
                                        )
                                    )
                            else:
                                attr = config_object[attr_name]

                        cascading = config_object
                        continue
                else:
                    break

        return attr

    def _walk_tree(self, data, scheme, ancestors=None, property_name=None, prefix=None):
        """ This function takes configuration data and a validation scheme
        then walk the configuration tree validating the configuraton data agenst
        the scheme provided. Will raise error on failure otherwise return None.

        Usage::
            >>> self._walk_tree(
            >>>    OrderedDict([('root', config_data)]),
            >>>    registries,
            >>>    REGISTRIES_SCHEME
            >>> )


        :param ancestors: A :OrderedDict:, The first element of the dict must be 'root'.
        :param data: The data that needs to be validated agents the scheme.
        :param scheme: A :dict:, The scheme defining the validations.
        :param property_name: A :string:, This is the name of the data getting validated.
        :param prefix:
        :rtype: :None: will raise error if a validation fails.
        """
        if property_name is None:
            property_name = 'root'
            # hack until i add this to references
            # reorder validates putting required first.  If the data doesn't exist there is no need to continue.
            order = ['registries'] + [key for key in scheme.keys() if key not in ('registries',)]
            scheme = OrderedDict(sorted(scheme.items(), key=lambda x: order.index(x[0])))

        if data is None:
            return

        elif not isinstance(property_name, six.string_types):
            raise TypeError('property_name must be a string.')

        ancestors = self._update_ancestors(data, property_name, ancestors)
        if isinstance(ancestors, OrderedDict):
            if list(ancestors)[0] != 'root':
                raise LookupError('root must be the first item in ancestors.')
        else:
            raise TypeError('ancestors must be an OrderedDict. {0} was passed'.format(type(ancestors)))

        if not isinstance(scheme, dict):
            raise TypeError('scheme must be a dict. {0} was passed.'.format(type(scheme)))
        scheme = self._update_scheme(scheme, ancestors)

        if property_name is not None and data:
            data = self._get_cascading_attr(
                property_name, *list(ancestors)[1:]
            ) if scheme.get('cascading', False) else data

        for err in self.__execute_validations(scheme.get('is', {}), data, property_name, ancestors, prefix=prefix):
            if err:
                raise err
            else:
                self._create_attr(property_name, data, ancestors)

        self.__validate_unrecognized_values(scheme, data, ancestors, prefix)

        self.__populate_scheme_references(scheme, property_name)

        self.__validate_config_properties(scheme, data, ancestors, prefix)

    def _update_ancestors(self, config_data, property_name, ancestors=None):
        """ Update ancestors for a specific property.

        :param ancestors: A :OrderedDict:, representing the ancestors of a property.
        :param config_data: The data that needs to be validated agents the scheme.
        :param property_name: A :string: of the properties name.
        :rtype: A :OrderDict: that has been updated with new parents.
        """
        if not isinstance(property_name, six.string_types):
            raise TypeError("property_key must be a string. type: {0} was passed.".format(type(property_name)))

        if ancestors is None:
            ancestors = OrderedDict([('root', config_data)])

        elif not isinstance(ancestors, OrderedDict):
            raise TypeError("ancestors must be an OrderedDict. type: {0} was passed.".format(type(ancestors)))

        elif 'root' not in ancestors:
            raise LookupError(
                'root must be in ancestors. currently in the ancestors chain {0}'.format(', '.join(ancestors.keys()))
            )

        ancestors = ancestors.copy()

        for previous_key in list(ancestors)[::-1]:
            previous_item = ancestors[previous_key]

            if isinstance(config_data, dict):
                if property_name in previous_item:
                    ancestors[property_name] = config_data
                    break

        return ancestors

    def _reference_keys(self, reference):
        """ Returns a list of all of keys for a given reference.

        :param reference: a :string:
        :rtype: A :list: of reference keys.
        """
        if not isinstance(reference, six.string_types):
            raise TypeError(
                'When using ~ to reference dynamic attributes ref must be a str. a {0} was provided.'.format(type(reference).__name__)
            )

        if '~' in reference:
            reference = reference[1:]

            scheme = self._scheme_references.get(reference)
            if not scheme:
                # TODO: need to create nice error here as well and print pretty message.
                raise LookupError(
                    "Was unable to find {0} in the scheme references. "
                    "available references {1}".format(reference, ', '.join(self._scheme_references.keys()))
                )

            return scheme['keys']
        else:
            raise AttributeError('references must start with ~. Please update {0} and retry.'.format(reference))

    def __populate_scheme_references(self, scheme, property_name):
        reference_scheme = scheme.get('ref')
        if reference_scheme:
            if reference_scheme in self._scheme_references:
                if property_name not in self._scheme_references[reference_scheme]['keys']:
                    self._scheme_references[reference_scheme]['keys'].append(property_name)
            else:
                self._scheme_references[reference_scheme] = {'keys': [property_name], 'scheme': scheme}

    def __validate_config_properties(self, scheme, data, ancestors, prefix=None):

        for scheme_key, child_scheme in six.iteritems(scheme):
            if scheme_key in RESERVED_SCHEME_KEYS:
                continue

            if isinstance(data, dict):
                if scheme_key in data or child_scheme.get('is', {}).get('required', False):
                    self._walk_tree(data.get(scheme_key), child_scheme.copy(), ancestors, scheme_key, prefix=prefix)
            else:
                # TODO: update error
                raise AttributeError(
                    '{0} is an unrecognized scheme key. replace with one of the following: {1}'.format(
                        scheme_key, ', '.join(RESERVED_SCHEME_KEYS)
                    )
                )

    def __validate_unrecognized_values(self, scheme, data, ancestors, prefix=None):
        unrecognized_values = self._collect_unrecognized_values(scheme, data, ancestors)
        default_scheme  = scheme.get('*')

        if unrecognized_values and default_scheme:
            for key in list(unrecognized_values):

                value = unrecognized_values.pop(key)
                try:
                    self._walk_tree(value, default_scheme.copy(), ancestors, key, prefix=prefix)
                except ConfigValidationException:
                    error = ConfigValidationException(ancestors, key, value, 'unrecognized', scheme)

                    if error.is_potential_fix_valid():
                        raise error
                    else:
                        raise

        if unrecognized_values:
            for key, value in six.iteritems(unrecognized_values):
                logger.info(
                    self.__build_validation_message(ancestors, key, 'unrecognized', key),
                    extra={'formatter': 'config-failure', 'prefix': prefix}
                )

                raise ConfigValidationException(ancestors, key, unrecognized_values, 'unrecognized', scheme)

    def __execute_validations(self, validations, data, property_name, ancestors, negation=False, prefix=None):
        """ Validate the data for a specific configuration value. This method will look up all of the validations provided
        and dynamically call any validation methods. If a validation fails a error will be thrown.  If no errors are found
        a attributes will be dynamically created on the Config object for the configuration value.

        :param validations: A :dict: with any required validations and expected values.
        :param data: the data to validate.
        :param property_name: A :string:, the properties name.
        :param ancestors: A :OrderedDict:, representing the ancestors of a property.
        """
        if not isinstance(ancestors, OrderedDict):
            raise TypeError("ancestors must be an OrderedDict. type: {0} was passed.".format(type(ancestors)))

        if not isinstance(validations, dict):
            raise TypeError('validations is required to be a dict. type: {1} was passed.'.format(type(validations)))

        if not isinstance(property_name, six.string_types):
            raise TypeError("property_key must be a string. type: {0} was passed.".format(type(property_name)))

        # reorder validates putting required first.  If the data doesn't exist there is no need to continue.
        order = ['type', 'required'] + [key for key in validations.keys() if key not in ('required', 'type')]
        ordered_validations = OrderedDict(sorted(validations.items(), key=lambda x: order.index(x[0])))

        for validation, value in six.iteritems(ordered_validations):
            if validation in VALIDATORS:

                if validation == 'not':
                    # TODO: need to test to make sure this works
                    for err in self.__execute_validations(value, data, property_name, ancestors, negation, prefix):
                        yield err

                    continue

                for err in getattr(self, '_{0}'.format(validation))(value, data, property_name, ancestors, negation, prefix):
                    yield err

            else:
                raise LookupError("{0} isn't a validator or reserved scheme key.".format(validation))

    def _type(self, expected, value, key, ancestors, negation, prefix):
        error     = None
        formatter = 'config-success'
        if isinstance(expected, tuple):
            data_type = []
            for dt in expected:
                if isinstance(dt, tuple):
                    data_type.extend([element for element in dt])
                else:
                    data_type.append(dt)

            data_type = ' or '.join([dt.__name__ for dt in data_type])
        else:
            data_type = expected.__name__

        # TODO: update not logic.
        if negation:
            if isinstance(value, expected):
                error = ConfigValidationException(ancestors, key, value, 'type', data_type)
                formatter = 'config-failure'

        elif not isinstance(value, expected):
            error = ConfigValidationException(ancestors, key, value, 'type', data_type)
            formatter = 'config-failure'

        logger.info(
            self.__build_validation_message(ancestors, key, 'type', data_type),
            extra={'formatter': formatter, 'prefix': prefix}
        )

        yield error

    def _required(self, expected, value, key, ancestors, negation, prefix):
        error = None
        if not isinstance(expected, (list, tuple)):
            raise TypeError('included is required to be a list or tuple. {0} was passed'.format(type(expected).__str__))

        matches = []

        for expected_key in expected:
            if not isinstance(expected_key, six.string_types):
                raise TypeError('each value in the included list must be a string.'.format(type(expected_key).__str__))

            if expected_key in value and value.get(expected_key) is not None:
                logger.info(
                    self.__build_validation_message(ancestors, key, 'required', expected_key),
                    extra={'formatter': 'config-success', 'prefix': prefix}
                )
            else:
                logger.info(
                    self.__build_validation_message(ancestors, key, 'required', expected_key),
                    extra={'formatter': 'config-failure', 'prefix': prefix}
                )
                matches.append(expected_key)

        if matches:
            error = ConfigValidationException(ancestors, key, value, 'required', matches)

        yield error

    def _items(self, expected, values, key, ancestors, negation, prefix):
        error = None
        items_prefix    = ' \u21B3'
        item_identifier = ' \u2605'

        if prefix:
            items_prefix = items_prefix.rjust(4)
            item_identifier = item_identifier.rjust(4)

        if isinstance(values, (list, tuple)):
            # validate each value.
            for i, value in enumerate(values):

                logger.info(
                    self.__build_validation_message(ancestors, key, 'item[{0}]'.format(i), value),
                    extra={'formatter': 'config-message', 'prefix': item_identifier}
                )

                try:
                    self._walk_tree(value, expected, ancestors, key, prefix=items_prefix)
                except ConfigValidationException as e:
                    error = e
        else:
            raise TypeError('Can\'t validate items if a list or tuple isn\'t passed.')

        yield error

    def _max(self, expected, value, key, ancestors, negation, prefix):
        """

        :param expected:
        :param value:
        :param key:
        :param ancestors:
        :param negation:
        :return:
        """
        error     = None
        formatter = 'config-success'
        length    = len(value) if value is not None else expected

        if length > expected:
            formatter = 'config-failure'
            error = ConfigValidationException(ancestors, key, value, 'max', expected)

        logger.info(
            self.__build_validation_message(ancestors, key, 'max', expected),
            extra={'formatter': formatter, 'prefix': prefix}
        )

        yield error

    def _one_of(self, expected, values, key, ancestors, negation, prefix):
        error         = None
        valid         = 0
        one_of_prefix = '  \u21B3'

        if prefix:
            one_of_prefix = one_of_prefix.rjust(4)

        if '~' in expected:
            expected = self._reference_keys(expected)

        logger.info(" \u2605 {0}".format(self.__build_validation_message(ancestors, key, 'one_of', '\u2605')))
        for i, expected_value in enumerate(expected):
            logger.info("  \u2605 {0}".format(
                self.__build_validation_message(ancestors, key, 'one_of', 'item[{0}]'.format(i)))
            )

            if isinstance(expected_value, dict):
                try:
                    self._walk_tree(values, expected_value, ancestors.copy(), key, prefix=one_of_prefix)

                    valid += 1
                    error = None

                except ConfigValidationException as e:
                    if not valid and error is None:
                        error = ConfigOneOfException(ancestors, key, values, 'one_of', None)
                        error.additional_messages.append(e.message)

                    pass
                except Exception:
                    pass
            else:
                if self.__one_of_validation(values, expected_value):
                    valid     += 1
                    error     = None
                    formatter = 'config-success'
                else:
                    formatter = 'config-failure'
                    if not valid:
                        error = ConfigValidationException(ancestors, key, values, 'one_of', expected)

                logger.info(
                    self.__build_validation_message(ancestors, key, 'one_of', expected_value),
                    extra={'formatter': formatter, 'prefix': one_of_prefix}
                )

        yield error

    def __one_of_validation(self, values, current_expected_value):
        if isinstance(values, (dict, list, tuple)):
            return values and current_expected_value in values
        else:
            return values and current_expected_value == values

    def _scheme_propagation(self, scheme, definitions):
        """ Will updated a scheme based on inheritance.  This is defined in a scheme objects with ``'inherit': '$definition'``.
        Will also updated parent objects for nested inheritance.

        Usage::
            >>> SCHEME = {
            >>>     'thing1': {
            >>>         'inherit': '$thing2'
            >>>     },
            >>>     '_': {
            >>>         'thing2': {
            >>>             'this_is': 'thing2 is a definition'
            >>>         }
            >>>     }
            >>> }
            >>> scheme = SCHEME.get('thing1')
            >>> if 'inherit' in scheme:
            >>>     scheme = self._scheme_propagation(scheme, SCHEME.get('_'))
            >>>
            >>> scheme.get('some_data')

        :param scheme: A dict, should be a scheme defining validation.
        :param definitions: A dict, should be defined in the scheme using '_'.
        :rtype: A :dict: will return a updated copy of the scheme.
        """
        if not isinstance(scheme, dict):
            raise TypeError('scheme must be a dict to propagate.')

        inherit_from = scheme.get('inherit')

        if isinstance(inherit_from, six.string_types):
            if not inherit_from.startswith('$'):
                raise AttributeError('When inheriting from an object it must start with a $.')

            if inherit_from.count('$') > 1:
                raise AttributeError('When inheriting an object it can only have one $.')

            if not isinstance(definitions, dict):
                raise AttributeError("Must define definitions in the root of the SCHEME. "
                                     "It is done so with  '_': { objs }.")
            name = inherit_from[1:]
            definition = definitions.copy().get(name)

            if not definition:
                raise LookupError(
                    'Was unable to find {0} in definitions. The follow are available: {1}.'.format(name, definitions)
                )

        else:
            raise AttributeError('inherit must be defined in your scheme and be a string value. format: $variable.')

        updated_scheme = {key: value for key, value in six.iteritems(scheme) if key not in definition}
        nested_scheme = None
        for key, value in six.iteritems(definition):
            if key in scheme:
                updated_scheme[key] = scheme[key]
            else:
                updated_scheme[key] = value

            if key == 'inherit':
                nested_scheme = self._scheme_propagation(definition, definitions)

        # remove inherit key
        if 'inherit' in updated_scheme:
            del updated_scheme['inherit']

        if nested_scheme is not None:
            updated_scheme.update(nested_scheme)

        return updated_scheme

    def __build_validation_message(self, ancestors, property_name, validation, expected_value):
        msg = " \u27A4 ".join(ancestors.keys())

        if isinstance(expected_value, dict):
            expected_value = expected_value.keys()

        if property_name == list(ancestors)[-1]:
            msg = "{0} \u27A4 {1}: {2}".format(msg, validation, expected_value)
        else:
            msg = '{0} \u27A4 {1} \u27A4 {2}: {3}'.format(msg, property_name, validation, expected_value)

        return msg


##
# Config Data Type Classes
##
class ConfigNode(object):
    def __init__(self, start_mark, end_mark):
        self._alias      = None
        self._name       = None
        self._start_mark = start_mark
        self._end_mark   = end_mark

    @property
    def alias(self):
        return self._alias

    @alias.setter
    def alias(self, value):
        if value is not None and not isinstance(value, six.string_types):
            raise TypeError('name must be a string.')

        self._alias = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is not None and not isinstance(value, six.string_types):
            raise TypeError('name must be a string.')
        self._name = value

    @property
    def start_mark(self):
        return self._start_mark

    @property
    def end_mark(self):
        return self._end_mark


class ConfigDict(dict, ConfigNode):
    def __init__(self, node_data, start_mark=None, end_mark=None):
        super(ConfigDict, self).__init__(node_data)
        ConfigNode.__init__(self, start_mark, end_mark)

    def __contains__(self, item):
        try:
            return super(ConfigDict, self).__contains__(item) or hasattr(self, item)
        except:
            return False

    def __delattr__(self, item):
        try:
            object.__getattribute__(self, item)
        except AttributeError:
            try:
                del self[item]
            except KeyError:
                raise AttributeError(item)
        else:
            object.__delattr__(self, item)

    def __getattr__(self, item):
        """
        """
        try:
            return object.__getattribute__(self, item)
        except:
            try:
                return self[item]
            except:
                raise AttributeError(item)

    def __setattr__(self, key, value):
        try:
            object.__getattribute__(self, key)
        except AttributeError:
            try:
                # allow for specific properties to be set on the base class and not be part of the dict.
                if key.startswith('_') and key[1:] in dir(self):
                    object.__setattr__(self, key, value)
                else:
                    self[key] = value
            except:
                raise AttributeError(key)
        else:
            object.__setattr__(self, key, value)


class ConfigSeq(list, ConfigNode):
    def __init__(self, node_data, start_mark=None, end_mark=None):
        list.__init__(self, node_data)
        ConfigNode.__init__(self, start_mark, end_mark)


class ConfigUnicode(str, ConfigNode):
    def __init__(self, node_data, start_mark=None, end_mark=None):
        ConfigNode.__init__(self, start_mark, end_mark)

    def __new__(cls, node_data, start_mark=None, end_mark=None):
        obj = super(ConfigUnicode, cls).__new__(cls, node_data)

        return obj


class ConfigInt(int, ConfigNode):
    def __init__(self, node_data, start_mark=None, end_mark=None):
        ConfigNode.__init__(self, start_mark, end_mark)

    def __new__(cls, node_data, start_mark=None, end_mark=None):
        return super(ConfigInt, cls).__new__(cls, node_data)


class ConfigFloat(float, ConfigNode):
    def __init__(self, node_data, start_mark=None, end_mark=None):
        ConfigNode.__init__(self, start_mark, end_mark)

    def __new__(cls, node_data, start_mark=None, end_mark=None):
        try:
            return float.__new__(cls, node_data)
        except TypeError:
            raise TypeError(node_data)
        except ValueError:
            raise ValueError(node_data)


##
# exception classes
##
class ConfigValidationException(Exception):
    def __init__(self, ancestors, property_name, data, validation_type, validation_value):
        self.ancestors          = ancestors
        self.data               = data
        self.property_name      = property_name
        self.validation_type    = validation_type
        self.validation_value   = validation_value
        self.parent_key         = list(self.ancestors)[-1]
        self.parent_value       = ancestors.get(self.parent_key)
        self._property_location = None
        self._potential_fixes   = []

        if isinstance(data, ConfigNode):
            self._property_location = 'line: {0} column: {1}.'.format(data.start_mark.line, data.start_mark.column)

        super(ConfigValidationException, self).__init__(self.message)

    @property
    def message(self):
        msg = '{0} failed validation: {1}.'.format(self.property_name, self.validation_type)

        if self._property_location:
            msg = '{0} {1}'.format(msg, self._property_location)

        fixes = self.potential_fixes()
        if fixes:
            msg = '{0} {1}'.format(msg, fixes)

        return msg

    def log_error(self):
        logger.error(self.message)

    def potential_fixes(self):
        # TODO: need to make this solid and provide better searching.
        potential_parent_fixes = None
        msg                    = ''

        if self.validation_type == 'unrecognized':
            potential_parent_fixes = self.__search_ancestors()

        if isinstance(self.validation_value, dict):
            self._potential_fixes = get_close_matches(self.property_name, self.validation_value.keys(), cutoff=0.5)

            if not self._potential_fixes:
                if potential_parent_fixes:
                    self._potential_fixes = potential_parent_fixes
                else:
                    self._potential_fixes = self.validation_value.keys()

        elif isinstance(self.validation_value, (list, tuple)):
            self._potential_fixes = get_close_matches(self.property_name, self.validation_value, cutoff=0.5)

            if not self._potential_fixes:
                if potential_parent_fixes:
                    self._potential_fixes = potential_parent_fixes
                else:
                    self._potential_fixes = self.validation_value
        else:
            self._potential_fixes.append(six.text_type(self.validation_value))

        if not msg:
            msg = 'Potential fixes in {0} add/delete/update {1}.'.format(self.property_name, ', '.join(self._potential_fixes))

        return msg if self._potential_fixes else None

    def is_potential_fix_valid(self):
        return bool(get_close_matches(self.property_name, self._potential_fixes, cutoff=0.6))

    @property
    def property_location(self):
        return self._property_location

    def __str__(self):
        return super(ConfigValidationException, self).__str__()

    def __search_ancestors(self):
        # TODO: fix messaging here.
        potential_fixes = []

        for ancestor_key, ancestor_item in six.iteritems(self.ancestors):
            if ancestor_key == self.parent_key:
                break

            for match in get_close_matches(self.parent_key, ancestor_item, cutoff=0.4):
                if match == self.parent_key:
                    continue

                potential_fixes.append(match)

        return potential_fixes


class ConfigOneOfException(ConfigValidationException):
    def __init__(self, ancestors, property_name, data, validation_type, validation_value):
        self.additional_messages = []
        self.property_name       = property_name
        super(ConfigOneOfException, self).__init__(ancestors, property_name, data, validation_type, validation_value)

    @property
    def message(self):
        msg = '{0} failed validation: {1}.'.format(self.property_name, self.validation_type)

        if self._property_location:
            msg = '{0} {1}'.format(msg, self._property_location)

        if self.additional_messages:
            msg = ' {0}\nPotential fixes:'.format(msg)

            for message in self.additional_messages:
                msg = '{0}\n    - {1}'.format(msg, message)

        return msg
