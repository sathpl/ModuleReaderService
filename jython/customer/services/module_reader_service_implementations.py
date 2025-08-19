# coding=utf-8

import logging

from .module_reader_service import ModuleReaderServiceImplementation

logger = logging.getLogger(__name__)

__all__ = ['CustomModuleReaderServiceImplementation']

class CustomModuleReaderServiceImplementation(ModuleReaderServiceImplementation):
    """
    CustomModuleReaderServiceImplementation
    """

    public = True

    def __init__(self, interface, method, variables, body, response, query_parameters, request_headers, request):
        super(CustomModuleReaderServiceImplementation, self).__init__(interface, method, variables, body, response, query_parameters, request_headers, request, target_module_id='100006')
