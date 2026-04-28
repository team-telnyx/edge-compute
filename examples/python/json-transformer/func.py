# JSON API Transformer Function
import logging
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Constants
HTTP_SCOPE_TYPE = 'http'


def new():
    """ New is the only method that must be implemented by a Function.
    The instance returned can be of any name.
    """
    return JSONTransformer()


class JSONTransformer:
    def __init__(self):
        """ Initialize the JSON transformer.
        """
        self.transformations = []  # Store transformation history

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
            await self._handle_info(send)
        elif method == 'GET' and path == '/transformations':
            await self._handle_list_transformations(send)
        elif method == 'POST' and path == '/transform':
            await self._handle_transform(scope, receive, send)
        elif method == 'POST' and path == '/transform/camel-to-snake':
            await self._handle_camel_to_snake(scope, receive, send)
        elif method == 'POST' and path == '/transform/snake-to-camel':
            await self._handle_snake_to_camel(scope, receive, send)
        elif method == 'POST' and path == '/transform/flatten':
            await self._handle_flatten(scope, receive, send)
        elif method == 'POST' and path == '/transform/filter':
            await self._handle_filter(scope, receive, send)
        elif method == 'POST' and path == '/transform/aggregate':
            await self._handle_aggregate(scope, receive, send)
        else:
            await self._handle_404(send)

    async def _handle_info(self, send):
        """ Handle API info endpoint.
        """
        response_data = {
            "service": "JSON API Transformer",
            "version": "1.0.0",
            "description": "Transform and process JSON data with various operations",
            "endpoints": [
                "GET  / - API information",
                "GET  /transformations - List transformation history",
                "POST /transform - Generic JSON transformation",
                "POST /transform/camel-to-snake - Convert camelCase to snake_case",
                "POST /transform/snake-to-camel - Convert snake_case to camelCase",
                "POST /transform/flatten - Flatten nested JSON",
                "POST /transform/filter - Filter JSON data",
                "POST /transform/aggregate - Aggregate JSON data"
            ],
            "features": [
                "Case conversion (camelCase ↔ snake_case)",
                "JSON flattening",
                "Data filtering and aggregation",
                "Custom transformation rules",
                "Transformation history tracking"
            ]
        }

        await self._send_json_response(send, 200, response_data)

    async def _handle_list_transformations(self, send):
        """ Handle listing transformation history.
        """
        response_data = {
            "transformations": self.transformations[-20:],  # Return last 20 transformations
            "total_transformations": len(self.transformations)
        }

        await self._send_json_response(send, 200, response_data)

    async def _handle_transform(self, scope, receive, send):
        """ Handle generic JSON transformation.
        """
        try:
            # Read request body
            body = await self._read_request_body(receive)
            request_data = json.loads(body.decode('utf-8'))

            # Extract transformation rules
            data = request_data.get('data', {})
            rules = request_data.get('rules', {})
            operation = request_data.get('operation', 'generic')

            # Apply transformation
            transformed_data = self._apply_transformation(data, rules, operation)

            # Store transformation record
            transformation_record = {
                "id": f"transform_{int(datetime.now().timestamp() * 1000)}",
                "timestamp": datetime.utcnow().isoformat(),
                "operation": operation,
                "rules": rules,
                "input_size": len(json.dumps(data)),
                "output_size": len(json.dumps(transformed_data))
            }

            self.transformations.append(transformation_record)

            await self._send_json_response(send, 200, {
                "message": "Transformation completed successfully",
                "transformation_id": transformation_record["id"],
                "operation": operation,
                "original_data": data,
                "transformed_data": transformed_data
            })

        except Exception as e:
            logging.error(f"Error in transformation: {e}")
            await self._send_json_response(send, 500, {
                "error": "Transformation failed",
                "message": str(e)
            })

    async def _handle_camel_to_snake(self, scope, receive, send):
        """ Handle camelCase to snake_case conversion.
        """
        try:
            body = await self._read_request_body(receive)
            data = json.loads(body.decode('utf-8'))
            
            transformed_data = self._convert_keys(data, self._camel_to_snake)

            await self._record_and_respond(send, "camel-to-snake", data, transformed_data)

        except Exception as e:
            await self._send_error_response(send, 500, "camel-to-snake conversion failed", str(e))

    async def _handle_snake_to_camel(self, scope, receive, send):
        """ Handle snake_case to camelCase conversion.
        """
        try:
            body = await self._read_request_body(receive)
            data = json.loads(body.decode('utf-8'))
            
            transformed_data = self._convert_keys(data, self._snake_to_camel)

            await self._record_and_respond(send, "snake-to-camel", data, transformed_data)

        except Exception as e:
            await self._send_error_response(send, 500, "snake-to-camel conversion failed", str(e))

    async def _handle_flatten(self, scope, receive, send):
        """ Handle JSON flattening.
        """
        try:
            body = await self._read_request_body(receive)
            data = json.loads(body.decode('utf-8'))
            
            separator = json.loads(body.decode('utf-8')).get('separator', '.')
            transformed_data = self._flatten_dict(data, separator)

            await self._record_and_respond(send, "flatten", data, transformed_data)

        except Exception as e:
            await self._send_error_response(send, 500, "Flattening failed", str(e))

    async def _handle_filter(self, scope, receive, send):
        """ Handle JSON filtering.
        """
        try:
            body = await self._read_request_body(receive)
            request_data = json.loads(body.decode('utf-8'))
            
            data = request_data.get('data', {})
            filters = request_data.get('filters', {})
            
            transformed_data = self._filter_data(data, filters)

            await self._record_and_respond(send, "filter", data, transformed_data)

        except Exception as e:
            await self._send_error_response(send, 500, "Filtering failed", str(e))

    async def _handle_aggregate(self, scope, receive, send):
        """ Handle JSON aggregation.
        """
        try:
            body = await self._read_request_body(receive)
            request_data = json.loads(body.decode('utf-8'))
            
            data = request_data.get('data', {})
            aggregations = request_data.get('aggregations', {})
            
            transformed_data = self._aggregate_data(data, aggregations)

            await self._record_and_respond(send, "aggregate", data, transformed_data)

        except Exception as e:
            await self._send_error_response(send, 500, "Aggregation failed", str(e))

    def _apply_transformation(self, data: Dict[str, Any], rules: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """ Apply generic transformation based on rules.
        """
        result = data.copy()
        
        for field, rule in rules.items():
            if field in result:
                if rule.get('type') == 'rename':
                    new_name = rule.get('to', field)
                    result[new_name] = result.pop(field)
                elif rule.get('type') == 'convert_case':
                    case_type = rule.get('case', 'snake')
                    if case_type == 'snake':
                        result[field] = self._camel_to_snake(result[field]) if isinstance(result[field], str) else result[field]
                    elif case_type == 'camel':
                        result[field] = self._snake_to_camel(result[field]) if isinstance(result[field], str) else result[field]
                elif rule.get('type') == 'format':
                    format_type = rule.get('format')
                    if format_type == 'uppercase' and isinstance(result[field], str):
                        result[field] = result[field].upper()
                    elif format_type == 'lowercase' and isinstance(result[field], str):
                        result[field] = result[field].lower()
        
        return result

    def _camel_to_snake(self, name: str) -> str:
        """ Convert camelCase to snake_case.
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _snake_to_camel(self, name: str) -> str:
        """ Convert snake_case to camelCase.
        """
        components = name.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])

    def _convert_keys(self, obj: Any, converter) -> Any:
        """ Recursively convert dictionary keys.
        """
        if isinstance(obj, dict):
            return {converter(k): self._convert_keys(v, converter) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_keys(item, converter) for item in obj]
        else:
            return obj

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """ Flatten nested dictionary.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _filter_data(self, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """ Filter data based on filter rules.
        """
        result = {}
        
        for key, value in data.items():
            include = True
            
            # Check include filters
            if 'include_fields' in filters:
                include = key in filters['include_fields']
            
            # Check exclude filters
            if include and 'exclude_fields' in filters:
                include = key not in filters['exclude_fields']
            
            # Check value filters
            if include and 'value_filters' in filters:
                for filter_key, filter_value in filters['value_filters'].items():
                    if key == filter_key:
                        if isinstance(filter_value, dict):
                            # Range filter
                            if 'min' in filter_value and value < filter_value['min']:
                                include = False
                            if 'max' in filter_value and value > filter_value['max']:
                                include = False
                        elif value != filter_value:
                            include = False
            
            if include:
                result[key] = value
        
        return result

    def _aggregate_data(self, data: Dict[str, Any], aggregations: Dict[str, Any]) -> Dict[str, Any]:
        """ Aggregate data based on aggregation rules.
        """
        result = {}
        
        for agg_name, agg_config in aggregations.items():
            field = agg_config.get('field')
            operation = agg_config.get('operation')
            
            if field in data:
                value = data[field]
                
                if operation == 'sum' and isinstance(value, (int, float, Decimal)):
                    result[agg_name] = value
                elif operation == 'count':
                    result[agg_name] = 1 if value is not None else 0
                elif operation == 'avg' and isinstance(value, (int, float, Decimal)):
                    result[agg_name] = value
                elif operation == 'min' and isinstance(value, (int, float, Decimal)):
                    result[agg_name] = value
                elif operation == 'max' and isinstance(value, (int, float, Decimal)):
                    result[agg_name] = value
                elif operation == 'concat' and isinstance(value, str):
                    result[agg_name] = value
        
        return result

    async def _read_request_body(self, receive):
        """ Read and return request body.
        """
        body = b''
        while True:
            message = await receive()
            if message['type'] == 'http.request':
                body += message.get('body', b'')
                if not message.get('more_body', False):
                    break
        return body

    async def _record_and_respond(self, send, operation: str, original_data: Any, transformed_data: Any):
        """ Record transformation and send response.
        """
        transformation_record = {
            "id": f"transform_{int(datetime.now().timestamp() * 1000)}",
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "input_size": len(json.dumps(original_data)),
            "output_size": len(json.dumps(transformed_data))
        }

        self.transformations.append(transformation_record)

        await self._send_json_response(send, 200, {
            "message": f"{operation} transformation completed successfully",
            "transformation_id": transformation_record["id"],
            "operation": operation,
            "original_data": original_data,
            "transformed_data": transformed_data
        })

    async def _send_error_response(self, send, status: int, error: str, message: str):
        """ Send error response.
        """
        await self._send_json_response(send, status, {
            "error": error,
            "message": message
        })

    async def _handle_404(self, send):
        """ Handle 404 responses.
        """
        await self._send_json_response(send, 404, {
            "error": "Not found",
            "message": "Endpoint not found"
        })

    async def _send_json_response(self, send, status: int, data: Dict[str, Any]):
        """ Send JSON response.
        """
        response_body = json.dumps(data, indent=2)

        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', b'application/json'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': response_body.encode(),
        })

    def start(self, cfg):
        """ Start the JSON transformer.
        """
        logging.info("JSON Transformer starting")

    def stop(self):
        """ Stop the JSON transformer.
        """
        logging.info("JSON Transformer stopping")
        logging.info(f"Processed {len(self.transformations)} transformations during this session")