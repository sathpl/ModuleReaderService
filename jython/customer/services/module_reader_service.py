# coding=utf-8

import logging
import json

# noinspection PyUnresolvedReferences
from java.util import HashMap
# noinspection PyUnresolvedReferences
from java.util import UUID as JavaUUID

from customizing import utilities
from customizing.weblink.exceptions import MandatoryAttributesMissingException
from customizing.weblink.interfaces.planta.base import ServiceImplementation
from customizing.weblink.enums import HTTPStatus

from customer.exceptions.module_reader import *
from customer.exceptions.transformer import *

logger = logging.getLogger(__name__)
session = utilities.ClientlessSession(user='PLSYSTEM')

__all__ = ['ModuleReaderServiceImplementation']

class ModuleReaderServiceImplementation(ServiceImplementation):
    """
    Interface for sending and receiving headdata
    """
    # available data:
    # self.interface = interface
    # self.method = method.upper()
    # self.variables = variables
    # self.body = body
    # self.response = response
    # self.query_parameters = query_parameters
    # self.request_headers = request_headers
    # self.request = request

    # entity_name = self.method.lower() + '_web_entity'
    # self.web_entity = getattr(self.interface, entity_name, None)

    public = True

    def __init__(self, interface, method, variables, body, response, query_parameters, request_headers, request, target_module_id=''):
        super(ModuleReaderServiceImplementation, self).__init__(interface, method, variables, body, response, query_parameters, request_headers, request)
        self.__target_module_id = target_module_id
        self.__errors = []

    def get(self):
        self.handle_get()

    def post(self):
        self.handle_post()

    def put(self):
        self.handle_put()

    def delete(self):
        self.handle_delete()

    def handle_get(self):
        try:
            receive_data = self._send_single(target_module_id=self.__target_module_id, request_type='GET', parsed_json=None)
        except (ModuleReaderModuleIDNotFoundException) as e:
            message = str(e)
            logger.error(message)
            self.update_response(status=HTTPStatus.INTERNAL_SERVER_ERROR, body=message)
            return
        except (TransformerException, ValueError) as e:
            message = str(e)
            logger.error(message)
            self.update_response(status=HTTPStatus.BAD_REQUEST, body=message)
            return

        if ('error' in receive_data.keys()):
            http_status = receive_data.get('status', HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            http_status = HTTPStatus.OK
        self.update_response(status=http_status, body=receive_data)

    def handle_post(self):
        """
        all data is available via member-variables, so no need to send these as parameters
        """
        # parsed_body = {} try isn't introducing a new scope, so declaration beforehand can be skipped
        self.__errors = []
        request_type = 'POST'

        try:
            parsed_body = json.loads(self.body)
        except ValueError as e:
            message = 'Could not parse body as JSON: {error}'.format(error=e)
            logger.error(message)
            self.update_response(status=HTTPStatus.BAD_REQUEST, body=message)
            return

        if not parsed_body:
            self.update_response(HTTPStatus.NO_CONTENT, "no data")
            return

        elif type(parsed_body) is dict:
            try:
                self._insist_mandatory_keys_exist(parsed_data=parsed_body, web_entity=self.web_entity, request_type=request_type)
                receive_data = self._send_single(target_module_id=self.__target_module_id, request_type=request_type, parsed_json=parsed_body)
            except (ModuleReaderModuleIDNotFoundException) as e:
                message = str(e)
                logger.error(message)
                self.update_response(status=HTTPStatus.INTERNAL_SERVER_ERROR, body=message)
                return
            except (TransformerException, ValueError) as e:
                message = str(e)
                logger.error(message)
                self.update_response(status=HTTPStatus.BAD_REQUEST, body=message)
                return
            except MandatoryAttributesMissingException as e:
                message = str(e.missing_attributes)
                logger.error(message)
                self.update_response(status=HTTPStatus.BAD_REQUEST, body=message)
                return
        elif type(parsed_body) is list:
            self._send_multiple(target_module_id=self.__target_module_id, request_type=request_type, parsed_jsons=parsed_body)

        if ('error' in receive_data.keys()):
            http_status = receive_data.get('status', HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            http_status = HTTPStatus.OK
        self.update_response(status=http_status, body=receive_data)

    def handle_put(self):
        """
        Prinzipiell das gleiche wie in POST, mit dem Unterschied, dass der zu editierende Datensatz
        - über die URL mitgegeben wird                  => self.variables['name']
        - existieren muss                               => Abfrage der Datenbank, wird im Modul durchgeführt
        Zudem muss der request-type angepasst werden    => body['#request_type'] = 'PUT'
        """
        # parsed_body = {} try isn't introducing a new scope, so declaration beforehand can be skipped
        self.__errors = []
        request_type = 'PUT'

        try:
            parsed_body = json.loads(self.body)
        except ValueError as e:
            message = 'Could not parse body as JSON: {error}'.format(error=e)
            logger.error(message)
            self.update_response(status=HTTPStatus.BAD_REQUEST, body=message)
            return

        if not parsed_body:
            self.update_response(HTTPStatus.NO_CONTENT, "no data")
            return
        elif type(parsed_body) is dict:
            try:
                self._insist_mandatory_keys_exist(parsed_data=parsed_body, web_entity=self.web_entity,
                                                  request_type=request_type)
                receive_data = self._send_single(target_module_id=self.__target_module_id, request_type=request_type,
                                                 parsed_json=parsed_body)
            except (ModuleReaderModuleIDNotFoundException) as e:
                message = str(e)
                logger.error(message)
                self.update_response(status=HTTPStatus.INTERNAL_SERVER_ERROR, body=message)
                return
            except (TransformerException, ValueError) as e:
                message = str(e)
                logger.error(message)
                self.update_response(status=HTTPStatus.BAD_REQUEST, body=message)
                return
            except MandatoryAttributesMissingException as e:
                message = str(e.missing_attributes)
                logger.error(message)
                self.update_response(status=HTTPStatus.BAD_REQUEST, body=message)
                return
        elif type(parsed_body) is list:
            self._send_multiple(target_module_id=self.__target_module_id, request_type=request_type, parsed_jsons=parsed_body)

        if ('error' in receive_data.keys()):
            http_status = receive_data.get('status', HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            http_status = HTTPStatus.OK
        self.update_response(status=http_status, body=receive_data)

    def handle_delete(self):
        prepared_data = {}
        prepared_data['#dt_number'] = self.web_entity.data_table
        prepared_data['#request_type'] = 'DELETE'

        for key in self.variables.keys():
            prepared_data['$'.join(key)] = self.variables[key]
        logger.info('query_parameters: {}'.format(self.query_parameters))
        for key in self.query_parameters.keys():
            prepared_data['%'.join(key)] = self.query_parameters[key]

        return prepared_data

    def _prepare_data_for_module_reader(self, request_type, parsed_data):
        """
        # prefix for metadata
        $ prefix for variables
        % prefix for query-parameters
        ! prefix for di_ids
        :return:
        """
        prepared_data = {}
        prepared_data['#dt_number'] = self.web_entity.data_table
        prepared_data['#request_type'] = request_type
        prepared_data['#web_entity'] = str(self.web_entity.uuid)
        prepared_data['!di_ids'] = self._get_di_ids()
        prepared_data['!di_pids'] = self._get_di_pids()
        logger.info('di_ids: {di_ids}'.format(di_ids=self._get_di_ids()))

        for key in self.variables.keys():
            prepared_data['${key}'.format(key=key)] = self.variables[key]

        for key in self.query_parameters.keys():
            prepared_data['%{key}'.format(key=key)] = self.query_parameters[key]

        # Prepare request-body-data for PUT and POST
        if request_type in ('POST', 'PUT'):
            mapped_data = self._map_attribute_dictionary_to_web_entity_attributes(attribute_dictionary=parsed_data, web_entity=self.web_entity)

            transformed_data = self.web_entity.transform_raw_values(mapped_attributes=mapped_data)

            prepared_data['#java_uuids'] = []
            prepared_data['#java_dates'] = []

            for key in transformed_data.keys():
                if type(transformed_data[key]) is JavaUUID:
                    prepared_data[key.python_id] = str(transformed_data[key])

                    prepared_data['#java_uuids'].append(key.python_id)
                elif type(transformed_data[key]) not in (bool, str, unicode, int, float, HashMap, list):
                    # todo: iterate over lists and test if these are clean
                    prepared_data[key.python_id] = parsed_data[key.attribute_name]
                    prepared_data['#java_dates'].append(key.python_id)
                else:
                    prepared_data[key.python_id] = transformed_data[key]

            if not prepared_data['#java_uuids']:
                prepared_data.pop('#java_uuids')
            if not prepared_data['#java_dates']:
                prepared_data.pop('#java_dates')

        return prepared_data

    def _send_single(self, target_module_id, request_type, parsed_json):
        """
        target_module_id as parameter because it cannot be set via gui and I want to avoid to force the user to
        overwrite the constructor
        """
        if not utilities.is_valid_module(target_module_id):
            raise ModuleReaderModuleIDNotFoundException('Module-ID {target_module_id} not found in database.'.format(target_module_id=target_module_id))

        data_send = self._prepare_data_for_module_reader(request_type=request_type, parsed_data=parsed_json)

        logger.debug('data_send: {}'.format(data_send))

        with session:
            session.open_module(module_id=target_module_id, parameters=data_send)
            receive_data = session.get_return_value(module_id=target_module_id, timeout=60)

        if receive_data is None:
            raise ModuleReaderProcessingModuleException("Module: {} returned no data".format(target_module_id))

        return receive_data
        # elif 'error' in receive_data:
        #     raise ModuleReaderProcessingModuleException("Errors occured during the request of module: {module_id} error: {error}".format(module_id=target_module_id, error=receive_data['error']))
        # else:
        #     return receive_data

    def _send_multiple(self, target_module_id, request_type, parsed_jsons):
        """
        Sollte _send_single interativ aufrufen
        :param target_module_id:
        :param request_type:
        :param parsed_jsons:
        :return:
        """
        if not utilities.is_valid_module(target_module_id):
            raise ModuleReaderModuleIDNotFoundException('Module-ID {target_module_id} not found in database.'.format(target_module_id=target_module_id))

        errors = []
        receive_data_items = []
        # loop
        for parsed_json in parsed_jsons:
            try:
                data_send = self._prepare_data_for_module_reader(request_type=request_type, parsed_data=parsed_json)
            except TransformerException as ex:
                message = "Transformationerror: {}".format(ex)
                logger.error(message)
                self.__errors.append(ex)
                return
            except ValueError as ex:
                message = "Transformationerror: {}".format(ex)
                logger.error(message)
                self.__errors.append(ex)
                return

            with session:
                session.open_module(module_id=target_module_id, parameters=data_send)
                receive_data = session.get_return_value(module_id=target_module_id, timeout=5)

            receive_data_items.append(receive_data)

            if receive_data is None:
                errors.append("Could not retrieve data from module: {}".format(target_module_id))
                continue

            elif 'error' in receive_data:
                errors.append("Errors occured during the request of module: {module_id} error: {error}".format(module_id=target_module_id, error=receive_data['error']))
                continue

        # ...loop

        if errors:
            logger.error("Errors occured during the request http-status: {status}, line: {line}".format(status=HTTPStatus.BAD_REQUEST, line='207'))
            self.update_response(HTTPStatus.BAD_REQUEST, body=self.__errors)
        else:
            self.update_response(HTTPStatus.OK, str(receive_data_items))

        return receive_data

    def _get_di_ids(self):
        uuid = str(self.web_entity.uuid).replace('-', '').upper()
        query = """
        SELECT dataitem FROM WebAttribute WHERE web_entity='{uuid}'
        """.format(uuid=uuid)
        res = utilities.db_select(query=query)
        return [rec[0] for rec in res]

    def _get_di_pids(self):
        logger.info('_get_di_pids debu info:')
        for web_attribute in self.web_entity.get_web_attributes():
            # logger.info('dataitem: {}'.format(web_attribute.dataitem))
            # logger.info('transformer_name: {}'.format(web_attribute.transformer_name))
            # logger.info('mandatory_put: {}'.format(web_attribute.mandatory_put))
            # logger.info('mandatory_post: {}'.format(web_attribute.mandatory_post))
            # logger.info('read_only: {}'.format(web_attribute.read_only))
            logger.info('python_id: {}'.format(web_attribute.python_id))
            logger.info('attribute_name: {}'.format(web_attribute.attribute_name))

        return [web_entity.python_id for web_entity in self.web_entity.get_web_attributes()]

    def _insist_mandatory_keys_exist(self, parsed_data, web_entity, request_type):
        web_attributes_keys = set(attribute.attribute_name for attribute in web_entity.get_web_attributes())
        parsed_data_keys = set(parsed_data.keys())
        #missing_keys = web_attributes_keys - parsed_data_keys
        if request_type == 'POST':
            missing_keys = [attribute.attribute_name    for attribute in web_entity.get_web_attributes()
                                                        if attribute.mandatory_post == True
                                                        and attribute.attribute_name not in parsed_data_keys]
        elif request_type == 'PUT':
            missing_keys = [attribute.attribute_name    for attribute in web_entity.get_web_attributes()
                                                        if attribute.mandatory_put == True
                                                        and attribute.attribute_name not in parsed_data_keys]

        if missing_keys:
            raise MandatoryAttributesMissingException('Missing keys: {}'.format(missing_keys))

    def _insist_readonly_keys_not_exist(self):
        pass