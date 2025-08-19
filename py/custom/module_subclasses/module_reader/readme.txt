Implementation of a custom servicehandler

The following tasks can be done through this interface:
- data sent through the ModuleReaderService can be decoded and be made available
  in subclasses


usage:

1) import ModuleReaderServiceHandler
2) create a new class which derives from ModuleReaderServiceHandler
3) the follwoing methods can be overwritten now:
   - handle_get(web_entity_uuid=web_entity_uuid, dt_number=dt_number, variables=variables, query_parameters=query_parameters, di_ids=di_ids, di_pids=di_pids)
   - handle_put(web_entity_uuid=web_entity_uuid, dt_number=dt_number, variables=variables, query_parameters=query_parameters, di_ids=di_ids, di_pids=di_pids, json_parameters=json_parameters)
   - handle_post(web_entity_uuid=web_entity_uuid, dt_number=dt_number, variables=variables, query_parameters=query_parameters, json_parameters=json_parameters)