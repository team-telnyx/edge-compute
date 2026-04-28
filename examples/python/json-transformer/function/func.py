# JSON Transformer Function
import logging
import json
import re
from typing import Dict, Any, List, Union
from datetime import datetime

# Constants
HTTP_SCOPE_TYPE = 'http'

def new():
    """ New is the only method that must be implemented by a Function.
    The instance returned can be of any name.
    """
    return JSONTransformer()

class JSONTransformer:
    def __init__(self):
        """ Initialize the JSON transformer with transformation history.
        """
        self.transformation_history = []  # In-memory history for demo
        self.custom_rules = {}  # Custom transformation rules

    def _camel_to_snake(self, name: str) -> str:
        """ Convert camelCase to snake_case. """
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return s1.lower()

    def _snake_to_camel(self, name: str) -> str:
        """ Convert snake_case to camelCase. """
        components = name.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])

    def _convert_keys(self, data: Union[Dict, List, Any], converter_func) -> Union[Dict, List, Any]:
        """ Recursively convert keys in nested dictionaries/lists. """
        if isinstance(data, dict):
            return {converter_func(key): self._convert_keys(value, converter_func) 
                   for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_keys(item, converter_func) for item in data]
        else:
            return data

    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
        """ Flatten nested dictionary. """
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, new_key, separator).items())
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}[{i}]", separator).items())
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, value))
        return dict(items)

    def _filter_data(self, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """ Filter data based on include/exclude rules. """
        result = {}
        
        include_keys = filters.get('include_keys', [])
        exclude_keys = filters.get('exclude_keys', [])
        include_values = filters.get('include_values', {})
        exclude_values = filters.get('exclude_values', {})
        value_filters = filters.get('value_filters', {})
        
        for key, value in data.items():
            include = True
            
            # Key filtering
            if include_keys and key not in include_keys:
                include = False
            if include and exclude_keys and key in exclude_keys:
                include = False
                
            # Value range filtering
            if include and value_filters:
                for filter_key, filter_config in value_filters.items():
                    if key == filter_key and isinstance(filter_config, dict):
                        if 'min' in filter_config and value < filter_config['min']:
                            include = False
                        if 'max' in filter_config and value > filter_config['max']:
                            include = False
                
            # Legacy value filtering
            if include and include_values:
                should_include = False
                for filter_key, filter_values in include_values.items():
                    if key == filter_key and value in filter_values:
                        should_include = True
                        break
                if not should_include:
                    include = False
                    
            if include and exclude_values:
                should_exclude = False
                for filter_key, filter_values in exclude_values.items():
                    if key == filter_key and value in filter_values:
                        should_exclude = True
                        break
                if should_exclude:
                    include = False
            
            if include:
                result[key] = value
            
        return result

    def _log_transformation(self, transformation_type: str, input_data: Any, output_data: Any):
        """ Log transformation for history tracking. """
        entry = {
            "id": f"transform_{int(datetime.utcnow().timestamp() * 1000)}",
            "timestamp": datetime.utcnow().isoformat(),
            "type": transformation_type,
            "input_size": len(json.dumps(input_data)) if isinstance(input_data, (dict, list)) else len(str(input_data)),
            "output_size": len(json.dumps(output_data)) if isinstance(output_data, (dict, list)) else len(str(output_data))
        }
        self.transformation_history.append(entry)
        
        # Keep only last 50 transformations
        if len(self.transformation_history) > 50:
            self.transformation_history = self.transformation_history[-50:]

    async def handle(self, scope, receive, send):
        """ Handle all HTTP requests to this JSON transformer.
        """
        # Validate ASGI scope for HTTP requests
        scope_request_type = scope.get('type')
        if scope_request_type is None or scope_request_type != HTTP_SCOPE_TYPE:
            logging.error("Invalid ASGI scope type: %s", scope_request_type)
            await send({
                'type': 'http.response.start',
                'status': 400,
                'headers': [[b'content-type', b'application/json']],
            })
            await send({
                'type': 'http.response.body',
                'body': json.dumps({"error": "Invalid request type"}).encode(),
            })
            return

        method = scope.get('method', 'GET')
        path = scope.get('path', '/')

        # Route handling
        if method == 'GET' and path == '/':
            await self._handle_api_info(send)
        elif method == 'GET' and path == '/health':
            await self._handle_health(send)
        elif method == 'GET' and path == '/history':
            await self._handle_history(send)
        elif method == 'POST' and path == '/transform/camel-to-snake':
            await self._handle_camel_to_snake(scope, receive, send)
        elif method == 'POST' and path == '/transform/snake-to-camel':
            await self._handle_snake_to_camel(scope, receive, send)
        elif method == 'POST' and path == '/transform/flatten':
            await self._handle_flatten(scope, receive, send)
        elif method == 'POST' and path == '/transform/filter':
            await self._handle_filter(scope, receive, send)
        elif method == 'POST' and path == '/transform/custom':
            await self._handle_custom_transform(scope, receive, send)
        elif method == 'POST' and path == '/transform/aggregate':
            await self._handle_aggregate(scope, receive, send)
        elif method == 'POST' and path == '/transform':
            await self._handle_generic_transform(scope, receive, send)
        elif method == 'GET' and path == '/transformations':
            await self._handle_transformations(send)
        else:
            await self._handle_404(send)

    async def _handle_api_info(self, send):
        """ Handle API info endpoint.
        """
        response_data = {
            "service": "JSON Transformer",
            "version": "1.0.0",
            "description": "Comprehensive JSON manipulation and transformation service",
            "endpoints": [
                "GET  / - API information",
                "GET  /health - Health check",
                "GET  /history - Transformation history",
                "POST /transform/camel-to-snake - Convert camelCase to snake_case",
                "POST /transform/snake-to-camel - Convert snake_case to camelCase", 
                "POST /transform/flatten - Flatten nested JSON objects",
                "POST /transform/filter - Filter JSON data based on rules",
                "POST /transform/custom - Apply custom transformation rules"
            ],
            "features": [
                "Case conversion (camelCase ↔ snake_case)",
                "JSON flattening with custom separators",
                "Advanced filtering with include/exclude rules",
                "Custom transformation rules",
                "Transformation history tracking",
                "Nested object/array support"
            ]
        }
        await self._send_json_response(send, 200, response_data)

    async def _handle_health(self, send):
        """ Handle health check endpoint.
        """
        response_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "transformations_performed": len(self.transformation_history),
            "custom_rules": len(self.custom_rules)
        }
        await self._send_json_response(send, 200, response_data)

    async def _handle_history(self, send):
        """ Handle transformation history endpoint.
        """
        response_data = {
            "history": self.transformation_history[-10:],  # Last 10 transformations
            "total_transformations": len(self.transformation_history)
        }
        await self._send_json_response(send, 200, response_data)

    async def _handle_camel_to_snake(self, scope, receive, send):
        """ Handle camelCase to snake_case conversion.
        """
        try:
            # Read request body
            body = await self._read_body(receive)
            data = json.loads(body.decode('utf-8'))
            
            # Transform data
            transformed_data = self._convert_keys(data, self._camel_to_snake)
            
            # Log transformation
            self._log_transformation("camel_to_snake", data, transformed_data)
            
            response_data = {
                "message": "Successfully converted camelCase to snake_case",
                "transformation": "camel_to_snake",
                "result": transformed_data
            }
            await self._send_json_response(send, 200, response_data)
            
        except json.JSONDecodeError:
            await self._send_json_response(send, 400, {
                "error": "Invalid JSON",
                "message": "Request body must contain valid JSON"
            })
        except Exception as e:
            logging.error(f"Error in camel-to-snake transformation: {e}")
            await self._send_json_response(send, 500, {
                "error": "Transformation failed",
                "message": str(e)
            })

    async def _handle_snake_to_camel(self, scope, receive, send):
        """ Handle snake_case to camelCase conversion.
        """
        try:
            body = await self._read_body(receive)
            data = json.loads(body.decode('utf-8'))
            
            transformed_data = self._convert_keys(data, self._snake_to_camel)
            self._log_transformation("snake_to_camel", data, transformed_data)
            
            response_data = {
                "message": "Successfully converted snake_case to camelCase",
                "transformation": "snake_to_camel", 
                "result": transformed_data
            }
            await self._send_json_response(send, 200, response_data)
            
        except json.JSONDecodeError:
            await self._send_json_response(send, 400, {
                "error": "Invalid JSON",
                "message": "Request body must contain valid JSON"
            })
        except Exception as e:
            logging.error(f"Error in snake-to-camel transformation: {e}")
            await self._send_json_response(send, 500, {
                "error": "Transformation failed",
                "message": str(e)
            })

    async def _handle_flatten(self, scope, receive, send):
        """ Handle JSON flattening.
        """
        try:
            body = await self._read_body(receive)
            request_data = json.loads(body.decode('utf-8'))
            
            # Extract data and options
            data = request_data.get('data', request_data)
            separator = request_data.get('separator', '.')
            
            if 'data' in request_data:
                # Structured request with options
                flattened_data = self._flatten_dict(data, '', separator)
            else:
                # Direct data flattening
                flattened_data = self._flatten_dict(request_data, '', separator)
                
            self._log_transformation("flatten", data, flattened_data)
            
            response_data = {
                "message": "Successfully flattened JSON structure",
                "transformation": "flatten",
                "options": {"separator": separator},
                "result": flattened_data
            }
            await self._send_json_response(send, 200, response_data)
            
        except json.JSONDecodeError:
            await self._send_json_response(send, 400, {
                "error": "Invalid JSON",
                "message": "Request body must contain valid JSON"
            })
        except Exception as e:
            logging.error(f"Error in flatten transformation: {e}")
            await self._send_json_response(send, 500, {
                "error": "Transformation failed",
                "message": str(e)
            })

    async def _handle_filter(self, scope, receive, send):
        """ Handle JSON filtering.
        """
        try:
            body = await self._read_body(receive)
            request_data = json.loads(body.decode('utf-8'))
            
            data = request_data.get('data', {})
            filters = request_data.get('filters', {})
            
            if not data:
                await self._send_json_response(send, 400, {
                    "error": "Missing data",
                    "message": "Request must include 'data' field"
                })
                return
                
            filtered_data = self._filter_data(data, filters)
            self._log_transformation("filter", data, filtered_data)
            
            response_data = {
                "message": "Successfully filtered JSON data",
                "transformation": "filter",
                "filters_applied": filters,
                "result": filtered_data
            }
            await self._send_json_response(send, 200, response_data)
            
        except json.JSONDecodeError:
            await self._send_json_response(send, 400, {
                "error": "Invalid JSON",
                "message": "Request body must contain valid JSON"
            })
        except Exception as e:
            logging.error(f"Error in filter transformation: {e}")
            await self._send_json_response(send, 500, {
                "error": "Transformation failed",
                "message": str(e)
            })

    async def _handle_custom_transform(self, scope, receive, send):
        """ Handle custom transformation rules.
        """
        try:
            body = await self._read_body(receive)
            request_data = json.loads(body.decode('utf-8'))
            
            data = request_data.get('data', {})
            rules = request_data.get('rules', [])
            
            transformed_data = data.copy()
            
            for rule in rules:
                rule_type = rule.get('type')
                if rule_type == 'rename_key':
                    old_key = rule.get('from')
                    new_key = rule.get('to')
                    if old_key in transformed_data:
                        transformed_data[new_key] = transformed_data.pop(old_key)
                elif rule_type == 'modify_value':
                    key = rule.get('key')
                    operation = rule.get('operation')
                    if key in transformed_data:
                        if operation == 'uppercase':
                            transformed_data[key] = str(transformed_data[key]).upper()
                        elif operation == 'lowercase':
                            transformed_data[key] = str(transformed_data[key]).lower()
                        elif operation == 'multiply' and 'factor' in rule:
                            transformed_data[key] = transformed_data[key] * rule['factor']
            
            self._log_transformation("custom", data, transformed_data)
            
            response_data = {
                "message": "Successfully applied custom transformation rules",
                "transformation": "custom",
                "rules_applied": rules,
                "result": transformed_data
            }
            await self._send_json_response(send, 200, response_data)
            
        except json.JSONDecodeError:
            await self._send_json_response(send, 400, {
                "error": "Invalid JSON",
                "message": "Request body must contain valid JSON"
            })
        except Exception as e:
            logging.error(f"Error in custom transformation: {e}")
            await self._send_json_response(send, 500, {
                "error": "Transformation failed",
                "message": str(e)
            })

    async def _handle_aggregate(self, scope, receive, send):
        """ Handle data aggregation.
        """
        try:
            body = await self._read_body(receive)
            request_data = json.loads(body.decode('utf-8'))
            
            data = request_data.get('data', {})
            aggregations = request_data.get('aggregations', {})
            
            if not data or not aggregations:
                await self._send_json_response(send, 400, {
                    "error": "Missing data or aggregations",
                    "message": "Request must include both 'data' and 'aggregations' fields"
                })
                return
                
            result = {}
            for agg_name, agg_config in aggregations.items():
                field = agg_config.get('field')
                operation = agg_config.get('operation')
                
                if field in data:
                    value = data[field]
                    if operation == 'sum':
                        result[agg_name] = value
                    elif operation == 'count':
                        result[agg_name] = 1 if value is not None else 0
                    elif operation == 'avg':
                        result[agg_name] = value  # Single value average
                    else:
                        result[agg_name] = value
            
            self._log_transformation("aggregate", data, result)
            
            response_data = {
                "message": "Successfully aggregated data",
                "transformation": "aggregate",
                "result": result
            }
            await self._send_json_response(send, 200, response_data)
            
        except json.JSONDecodeError:
            await self._send_json_response(send, 400, {
                "error": "Invalid JSON",
                "message": "Request body must contain valid JSON"
            })
        except Exception as e:
            logging.error(f"Error in aggregate transformation: {e}")
            await self._send_json_response(send, 500, {
                "error": "Transformation failed",
                "message": str(e)
            })

    async def _handle_generic_transform(self, scope, receive, send):
        """ Handle generic transformation with rules.
        """
        try:
            body = await self._read_body(receive)
            request_data = json.loads(body.decode('utf-8'))
            
            data = request_data.get('data', {})
            rules = request_data.get('rules', {})
            operation = request_data.get('operation', 'generic')
            
            # Apply transformation rules
            result = data.copy()
            for field, rule in rules.items():
                if field in result and isinstance(rule, dict):
                    rule_type = rule.get('type')
                    if rule_type == 'format':
                        format_type = rule.get('format')
                        if format_type == 'uppercase':
                            result[field] = str(result[field]).upper()
                        elif format_type == 'lowercase':
                            result[field] = str(result[field]).lower()
                    elif rule_type == 'rename':
                        new_name = rule.get('to', field)
                        result[new_name] = result.pop(field)
                        
            self._log_transformation(operation, data, result)
            
            response_data = {
                "message": "Transformation completed successfully",
                "transformation_id": f"transform_{int(datetime.utcnow().timestamp() * 1000)}",
                "operation": operation,
                "original_data": data,
                "transformed_data": result
            }
            await self._send_json_response(send, 200, response_data)
            
        except json.JSONDecodeError:
            await self._send_json_response(send, 400, {
                "error": "Invalid JSON", 
                "message": "Request body must contain valid JSON"
            })
        except Exception as e:
            logging.error(f"Error in generic transformation: {e}")
            await self._send_json_response(send, 500, {
                "error": "Transformation failed",
                "message": str(e)
            })

    async def _handle_transformations(self, send):
        """ Handle transformation history endpoint.
        """
        response_data = {
            "transformations": self.transformation_history[-20:],  # Return last 20 transformations
            "total_transformations": len(self.transformation_history)
        }
        await self._send_json_response(send, 200, response_data)

    async def _handle_404(self, send):
        """ Handle 404 responses.
        """
        await self._send_json_response(send, 404, {
            "error": "Not found",
            "message": "Endpoint not found"
        })

    async def _read_body(self, receive):
        """ Read request body from ASGI receive callable.
        """
        body = b''
        while True:
            message = await receive()
            if message['type'] == 'http.request':
                body += message.get('body', b'')
                if not message.get('more_body', False):
                    break
        return body

    async def _send_json_response(self, send, status: int, data: Dict[str, Any]):
        """ Send JSON response.
        """
        response_body = json.dumps(data, indent=2)

        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', b'application/json'],
                [b'access-control-allow-origin', b'*'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': response_body.encode(),
        })

    def start(self, cfg):
        """ Start the JSON transformer and load configuration.
        """
        logging.info("JSON Transformer starting")
        
        # Load any custom configuration
        max_history = cfg.get('MAX_HISTORY_SIZE', '50')
        try:
            max_history = int(max_history)
            if max_history > 0:
                self.max_history = max_history
        except (ValueError, TypeError):
            self.max_history = 50
            
        logging.info(f"JSON Transformer configured with max history size: {self.max_history}")

    def stop(self):
        """ Stop the JSON transformer.
        """
        logging.info("JSON Transformer stopping")
        logging.info(f"Processed {len(self.transformation_history)} transformations during this session")