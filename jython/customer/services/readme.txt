Implementation of a custom service

The following tasks can be done through this interface:

- check if the module exists and can be used by the service
- convert non-primitive datatypes to strings that cannot be sent through the interface (data, uuid)
- send type-information with the jason-file for converting non-primitives back later
- check if mandatory PUT and mandatory GET parameters are given in the body
- sending the data of the body
- sending the query-parameters
- sending the variables
- send metadata:
  - request-type
  - uuid of webentity
  - number of the datatable
- automatically return status-codes and generate error message in case of failure

1) import ModuleReaderServiceImplementation
2) create a new class which derives from ModuleReaderServiceImplementation
3) overwrite the __init__-method and call the super-method with the mandatory parameters:

    def __init__(self, interface, method, variables, body, response, query_parameters, request_headers, request):
        super(CustomModuleReaderServiceImplementation, self).__init__(  interface,
                                                                        method,
                                                                        variables,
                                                                        body,
                                                                        response,
                                                                        query_parameters,
                                                                        request_headers,
                                                                        request,
                                                                        target_module_id='<id>')

4) the "target_module_id" was added for introducing the id of the macro-module which receives the data

The above steps are only necessary to announce the target_module_id to the Webservice.
Alternatively the target_module_id could be specified through the GUI. For that an additional
field would have to be added to the GUI for enabling the possibility to enter the id to the
user.
That's it, nothing else has to be done on jython side.




