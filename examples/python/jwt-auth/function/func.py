# JWT Authentication Function
import logging
import json
import jwt
import hashlib
import hmac
import secrets
import time
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
import base64

# Constants
HTTP_SCOPE_TYPE = 'http'


def new():
    """ New is the only method that must be implemented by a Function.
    The instance returned can be of any name.
    """
    return JWTAuthenticator()


class JWTAuthenticator:
    def __init__(self):
        """ Initialize the JWT authenticator with configuration.
        """
        self.jwt_secret = None
        self.jwt_algorithm = 'HS256'
        self.token_expiry_minutes = 60
        self.refresh_expiry_days = 7
        self.users = {}  # In-memory user store for demo
        self.refresh_tokens = {}  # In-memory refresh token store
        
        # Add some demo users
        self._init_demo_users()

    def _init_demo_users(self):
        """ Initialize demo users for testing.
        """
        # Create users with secure password hashing
        admin_salt, admin_hash = self._hash_password('admin123')
        user1_salt, user1_hash = self._hash_password('password123') 
        demo_salt, demo_hash = self._hash_password('demo123')
        
        self.users = {
            'admin': {
                'user_id': 'admin',
                'password_hash': admin_hash,
                'password_salt': admin_salt,
                'email': 'admin@example.com',
                'roles': ['admin', 'user'],
                'created_at': datetime.utcnow().isoformat()
            },
            'user1': {
                'user_id': 'user1', 
                'password_hash': user1_hash,
                'password_salt': user1_salt,
                'email': 'user1@example.com',
                'roles': ['user'],
                'created_at': datetime.utcnow().isoformat()
            },
            'demo': {
                'user_id': 'demo',
                'password_hash': demo_hash,
                'password_salt': demo_salt,
                'email': 'demo@example.com', 
                'roles': ['user', 'demo'],
                'created_at': datetime.utcnow().isoformat()
            }
        }

    def _hash_password(self, password: str) -> tuple[str, str]:
        """ Hash password using SHA-256 with random salt per password.
        Returns (salt, hash) tuple for secure storage.
        
        ⚠️ SECURITY WARNING: SHA-256 is NOT recommended for production password hashing!
        Use bcrypt (recommended), argon2, or scrypt instead. SHA-256 is too fast and
        vulnerable to GPU-based brute force attacks.
        
        For production:
        pip install bcrypt
        import bcrypt
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        """
        # Generate a random 32-byte salt for this password
        salt = secrets.token_hex(32)
        
        # Hash the password with the salt
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        return salt, password_hash

    def _verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        """ Verify password against stored hash and salt.
        """
        # Hash the provided password with the stored salt
        test_hash = hashlib.sha256((password + stored_salt).encode()).hexdigest()
        
        # Compare hashes securely
        return hmac.compare_digest(test_hash, stored_hash)

    def _generate_jwt_token(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """ Generate JWT access token and refresh token.
        """
        now = datetime.now(timezone.utc)
        access_payload = {
            'user_id': user_data['user_id'],
            'email': user_data['email'],
            'roles': user_data['roles'],
            'iat': now,
            'exp': now + timedelta(minutes=self.token_expiry_minutes),
            'type': 'access'
        }
        
        refresh_payload = {
            'user_id': user_data['user_id'],
            'iat': now,
            'exp': now + timedelta(days=self.refresh_expiry_days),
            'type': 'refresh'
        }

        access_token = jwt.encode(access_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        refresh_token = jwt.encode(refresh_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Store refresh token
        self.refresh_tokens[refresh_token] = {
            'user_id': user_data['user_id'],
            'created_at': now.isoformat()
        }
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': self.token_expiry_minutes * 60,
            'expires_at': (now + timedelta(minutes=self.token_expiry_minutes)).isoformat()
        }

    def _verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """ Verify and decode JWT token.
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}

    def _extract_bearer_token(self, headers: Dict[bytes, bytes]) -> Optional[str]:
        """ Extract Bearer token from Authorization header.
        """
        auth_header = headers.get(b'authorization', b'').decode('utf-8')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        return None

    async def handle(self, scope, receive, send):
        """ Handle all HTTP requests to this JWT authenticator.
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
        headers = dict(scope.get('headers', []))

        # Route handling
        if method == 'GET' and path == '/':
            await self._handle_info(send)
        elif method == 'POST' and path == '/auth/login':
            await self._handle_login(scope, receive, send)
        elif method == 'POST' and path == '/auth/refresh':
            await self._handle_refresh(scope, receive, send)
        elif method == 'POST' and path == '/auth/logout':
            await self._handle_logout(scope, receive, send)
        elif method == 'GET' and path == '/auth/me':
            await self._handle_me(headers, send)
        elif method == 'GET' and path == '/protected':
            await self._handle_protected(headers, send)
        elif method == 'GET' and path == '/admin':
            await self._handle_admin(headers, send)
        elif method == 'GET' and path == '/users':
            await self._handle_list_users(headers, send)
        else:
            await self._handle_404(send)

    async def _handle_info(self, send):
        """ Handle API info endpoint.
        """
        response_data = {
            "service": "JWT Authentication Service",
            "version": "1.0.0",
            "description": "JWT-based authentication and authorization service",
            "endpoints": [
                "GET  / - API information",
                "POST /auth/login - Authenticate user and get tokens",
                "POST /auth/refresh - Refresh access token",
                "POST /auth/logout - Logout and invalidate tokens",
                "GET  /auth/me - Get current user info (requires auth)",
                "GET  /protected - Protected endpoint (requires auth)",
                "GET  /admin - Admin endpoint (requires admin role)",
                "GET  /users - List users (requires admin role)"
            ],
            "authentication": {
                "type": "JWT Bearer Token",
                "header": "Authorization: Bearer <access_token>",
                "token_expiry": f"{self.token_expiry_minutes} minutes",
                "refresh_expiry": f"{self.refresh_expiry_days} days"
            },
            "demo_users": [
                {"username": "admin", "password": "admin123", "roles": ["admin", "user"]},
                {"username": "user1", "password": "password123", "roles": ["user"]},
                {"username": "demo", "password": "demo123", "roles": ["user", "demo"]}
            ]
        }

        await self._send_json_response(send, 200, response_data)

    async def _handle_login(self, scope, receive, send):
        """ Handle user login and token generation.
        """
        try:
            body = await self._read_request_body(receive)
            login_data = json.loads(body.decode('utf-8'))

            username = login_data.get('username', '').strip()
            password = login_data.get('password', '')

            if not username or not password:
                await self._send_json_response(send, 400, {
                    "error": "Missing credentials",
                    "message": "Username and password are required"
                })
                return

            # Check user exists and verify password
            user = self.users.get(username)
            if not user or not self._verify_password(password, user['password_hash'], user['password_salt']):
                await self._send_json_response(send, 401, {
                    "error": "Invalid credentials",
                    "message": "Username or password is incorrect"
                })
                return

            # Generate tokens
            tokens = self._generate_jwt_token(user)

            await self._send_json_response(send, 200, {
                "message": "Login successful",
                "user": {
                    "user_id": user['user_id'],
                    "email": user['email'],
                    "roles": user['roles']
                },
                **tokens
            })

        except Exception as e:
            logging.error(f"Login error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Login failed",
                "message": str(e)
            })

    async def _handle_refresh(self, scope, receive, send):
        """ Handle token refresh.
        """
        try:
            body = await self._read_request_body(receive)
            refresh_data = json.loads(body.decode('utf-8'))

            refresh_token = refresh_data.get('refresh_token', '').strip()
            if not refresh_token:
                await self._send_json_response(send, 400, {
                    "error": "Missing refresh token",
                    "message": "Refresh token is required"
                })
                return

            # Verify refresh token
            payload = self._verify_jwt_token(refresh_token)
            if not payload or payload.get('error') or payload.get('type') != 'refresh':
                await self._send_json_response(send, 401, {
                    "error": "Invalid refresh token",
                    "message": "Refresh token is invalid or expired"
                })
                return

            # Check if refresh token exists in our store
            if refresh_token not in self.refresh_tokens:
                await self._send_json_response(send, 401, {
                    "error": "Invalid refresh token",
                    "message": "Refresh token not found"
                })
                return

            # Get user data
            user_id = payload['user_id']
            user = self.users.get(user_id)
            if not user:
                await self._send_json_response(send, 404, {
                    "error": "User not found",
                    "message": "User associated with token not found"
                })
                return

            # Generate new tokens
            tokens = self._generate_jwt_token(user)
            
            # Remove old refresh token
            del self.refresh_tokens[refresh_token]

            await self._send_json_response(send, 200, {
                "message": "Token refreshed successfully",
                **tokens
            })

        except Exception as e:
            logging.error(f"Refresh error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Token refresh failed",
                "message": str(e)
            })

    async def _handle_logout(self, scope, receive, send):
        """ Handle user logout.
        """
        try:
            body = await self._read_request_body(receive)
            logout_data = json.loads(body.decode('utf-8'))

            refresh_token = logout_data.get('refresh_token', '').strip()
            
            # Remove refresh token if provided
            if refresh_token and refresh_token in self.refresh_tokens:
                del self.refresh_tokens[refresh_token]

            await self._send_json_response(send, 200, {
                "message": "Logout successful"
            })

        except Exception as e:
            logging.error(f"Logout error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Logout failed",
                "message": str(e)
            })

    async def _handle_me(self, headers: Dict[bytes, bytes], send):
        """ Handle current user info endpoint.
        """
        # Verify authentication
        auth_result = await self._verify_authentication(headers)
        if not auth_result['authenticated']:
            await self._send_json_response(send, auth_result['status'], {
                "error": auth_result['error'],
                "message": auth_result['message']
            })
            return

        payload = auth_result['payload']
        user = self.users.get(payload['user_id'])
        
        await self._send_json_response(send, 200, {
            "user": {
                "user_id": user['user_id'],
                "email": user['email'],
                "roles": user['roles'],
                "created_at": user['created_at']
            },
            "token_info": {
                "issued_at": payload['iat'],
                "expires_at": payload['exp'],
                "type": payload['type']
            }
        })

    async def _handle_protected(self, headers: Dict[bytes, bytes], send):
        """ Handle protected endpoint requiring authentication.
        """
        auth_result = await self._verify_authentication(headers)
        if not auth_result['authenticated']:
            await self._send_json_response(send, auth_result['status'], {
                "error": auth_result['error'],
                "message": auth_result['message']
            })
            return

        payload = auth_result['payload']
        
        await self._send_json_response(send, 200, {
            "message": "Access granted to protected resource",
            "user_id": payload['user_id'],
            "roles": payload['roles'],
            "data": {
                "secret": "This is protected data",
                "timestamp": datetime.utcnow().isoformat(),
                "access_level": "standard"
            }
        })

    async def _handle_admin(self, headers: Dict[bytes, bytes], send):
        """ Handle admin endpoint requiring admin role.
        """
        auth_result = await self._verify_authentication(headers, required_roles=['admin'])
        if not auth_result['authenticated']:
            await self._send_json_response(send, auth_result['status'], {
                "error": auth_result['error'],
                "message": auth_result['message']
            })
            return

        payload = auth_result['payload']
        
        await self._send_json_response(send, 200, {
            "message": "Admin access granted",
            "user_id": payload['user_id'],
            "admin_data": {
                "total_users": len(self.users),
                "active_refresh_tokens": len(self.refresh_tokens),
                "system_status": "operational",
                "timestamp": datetime.utcnow().isoformat()
            }
        })

    async def _handle_list_users(self, headers: Dict[bytes, bytes], send):
        """ Handle list users endpoint (admin only).
        """
        auth_result = await self._verify_authentication(headers, required_roles=['admin'])
        if not auth_result['authenticated']:
            await self._send_json_response(send, auth_result['status'], {
                "error": auth_result['error'],
                "message": auth_result['message']
            })
            return

        # Return user list without sensitive information
        users_list = []
        for user_id, user_data in self.users.items():
            users_list.append({
                "user_id": user_data['user_id'],
                "email": user_data['email'],
                "roles": user_data['roles'],
                "created_at": user_data['created_at']
            })

        await self._send_json_response(send, 200, {
            "users": users_list,
            "total_users": len(users_list)
        })

    async def _verify_authentication(self, headers: Dict[bytes, bytes], required_roles: Optional[List[str]] = None) -> Dict[str, Any]:
        """ Verify JWT authentication and optional role requirements.
        """
        token = self._extract_bearer_token(headers)
        if not token:
            return {
                'authenticated': False,
                'status': 401,
                'error': 'Missing token',
                'message': 'Authorization header with Bearer token is required'
            }

        payload = self._verify_jwt_token(token)
        if not payload:
            return {
                'authenticated': False,
                'status': 401,
                'error': 'Invalid token',
                'message': 'Token verification failed'
            }
            
        if payload.get('error'):
            return {
                'authenticated': False,
                'status': 401,
                'error': 'Token error',
                'message': payload['error']
            }

        if payload.get('type') != 'access':
            return {
                'authenticated': False,
                'status': 401,
                'error': 'Wrong token type',
                'message': 'Access token is required'
            }

        # Check role requirements
        if required_roles:
            user_roles = payload.get('roles', [])
            if not any(role in user_roles for role in required_roles):
                return {
                    'authenticated': False,
                    'status': 403,
                    'error': 'Insufficient permissions',
                    'message': f'Required roles: {required_roles}'
                }

        return {
            'authenticated': True,
            'payload': payload
        }

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
        response_body = json.dumps(data, indent=2, default=str)

        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', b'application/json'],
                [b'access-control-allow-origin', b'*'],
                [b'access-control-allow-methods', b'GET, POST, OPTIONS'],
                [b'access-control-allow-headers', b'Authorization, Content-Type'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': response_body.encode(),
        })

    def start(self, cfg):
        """ Start the JWT authenticator and load configuration.
        """
        logging.info("JWT Authenticator starting")
        
        # Load JWT secret from environment or config
        self.jwt_secret = cfg.get('JWT_SECRET') or cfg.get('jwt_secret') or 'default-jwt-secret-change-in-production'
        
        # Load other configuration
        self.jwt_algorithm = cfg.get('JWT_ALGORITHM', 'HS256')
        self.token_expiry_minutes = int(cfg.get('JWT_EXPIRY_MINUTES', '60'))
        self.refresh_expiry_days = int(cfg.get('JWT_REFRESH_EXPIRY_DAYS', '7'))
        
        if self.jwt_secret == 'default-jwt-secret-change-in-production':
            logging.error("❌ CRITICAL: Using default JWT secret is insecure!")
            # Prevent production deployment with default secret
            import os
            if os.getenv('ENVIRONMENT', 'development').lower() == 'production':
                raise ValueError("JWT_SECRET must be configured for production deployment")
            logging.warning("⚠️ Using default JWT secret - ONLY acceptable for local development")
        else:
            logging.info("JWT secret configured from environment")
            
        logging.info(f"JWT configuration: algorithm={self.jwt_algorithm}, expiry={self.token_expiry_minutes}min")

    def stop(self):
        """ Stop the JWT authenticator.
        """
        logging.info("JWT Authenticator stopping")
        logging.info(f"Active refresh tokens: {len(self.refresh_tokens)}")