from uuid import UUID

from ppms import ppms
from ppms.sql import convert_date_to_planta_time, sanitize_value
from ppms.module_subclasses.base_class import Base

class ModuleReaderServiceHandler(Base):
    def on_web_load(self, parameters):
        """
        Empfängt Daten von einer Webschnittstelle
        :param parameters:
        special keys:
        '#request_type'     => type of the request, must be set in the WebServiceImplementation
        '#raw_value_keys'   => values that have to be converted because the origin type cannot be sent because it is not
                               a primitive
        :return:
        """
        #return {'test': 'ok'}
        date_format = '%d.%m.%Y'

        response = {}
        response.update(parameters)
        ppms.logger.info(f'parameters incoming: {parameters}')
        # extract additional key / value-pairs
        try:
            request_type = parameters.pop(u'#request_type')
        except KeyError:
            response['error'] = 'Request type missing, unable to compute service request'
            response['status'] = 500
            return response

        try:
            dt_number = int(parameters.pop(u'#dt_number'))
        except KeyError:
            response['error'] = 'Datatable number missing, unable to compute service request'
            response['status'] = 500
            return response
        except ValueError:
            response['error'] = 'Datatable number invalid, unable to compute service request'
            response['status'] = 500
            return response

        try:
            web_entity_uuid = sanitize_value(UUID(parameters.pop(u'#web_entity')))
        except KeyError:
            response['error'] = 'Webentity UUID missing, unable to compute service request'
            response['status'] = 500
            return response
        except ValueError:
            response['error'] = 'Webentity UUID invalid, unable to compute service request'
            response['status'] = 500
            return response

        di_ids = parameters.pop(u'!di_ids', [])
        di_pids = parameters.pop(u'!di_pids', [])

        java_uuids = parameters.pop(u'#java_uuids', [])
        for java_uuid in java_uuids:
            if parameters[java_uuid] == '':
                parameters.pop(java_uuid)
                continue
            parameters[java_uuid] = sanitize_value(UUID(parameters[java_uuid]))

        java_dates = parameters.pop(u'#java_dates', [])
        for java_date in java_dates:
            if parameters[java_date] == '':
                parameters.pop(java_date)
                continue
            parameters[java_date] = convert_date_to_planta_time(parameters[java_date])

        variables = {}
        query_parameters = {}
        json_parameters = {}
        for key in parameters:
            if key[0] not in ('#', '$', '%', '!'):
                """
                Es werden die python-dis als key verwendet, nicht die attribute_names
                Evt. könnte man eine eigene Dictionary-Datenstruktur entwerfen, die den
                Zugriff auf einen value über mehrere keys erlaubt (di,python-di,attribute_name)
                """
                json_parameters[key] = parameters[key]
            else:
                if key.startswith('$'):
                    variables[key[1:]] = parameters[key]

                if key.startswith('%'):
                    query_parameters[key[1:]] = parameters[key]

        if request_type == 'GET':
            response = self.handle_get(web_entity_uuid=web_entity_uuid, dt_number=dt_number, variables=variables, query_parameters=query_parameters, di_ids=di_ids, di_pids=di_pids)
            if not response:
                response = {}
                response['error'] = 'Could not handle GET request'
        if request_type == 'PUT':
            response = self.handle_put(web_entity_uuid=web_entity_uuid, dt_number=dt_number, variables=variables, query_parameters=query_parameters, di_ids=di_ids, di_pids=di_pids, json_parameters=json_parameters)
            if not response:
                response = {}
                response['error'] = 'Could not handle PUT request'
        if request_type == 'POST':
            response = self.handle_post(web_entity_uuid=web_entity_uuid, dt_number=dt_number, variables=variables, query_parameters=query_parameters, json_parameters=json_parameters)
            if not response:
                response = {}
                response['error'] = 'Could not handle POST request'
        # if request_type == 'DELETE':
        #     parameters['success'] = self.handle_delete(parameters)
        #self.menu(135)
        return response

    def handle_get(self, *args, **kwargs):
        raise NotImplementedError()

    def handle_put(self, *args, **kwargs):
        raise NotImplementedError()

    def handle_post(self, *args, **kwargs):
        raise NotImplementedError()

    def handle_delete(self, *args, **kwargs):
        raise NotImplementedError()

    def _get_attribute_name_from_di_python_id(self, web_entity_uuid, dt_number, di_python_id):
        query = f"""
        SELECT NAME FROM WEBATTRIBUTE 
        WHERE WEB_ENTITY='{web_entity_uuid}' 
        AND DATAITEM=(SELECT DI000238 FROM DT412 WHERE DI000239='{dt_number}' AND DI041035='{di_python_id}')
        """
        res = ppms.db_select(query=query)
        return res[0][0]