# JWT Authentication

A comprehensive JWT-based authentication and authorization service built for Telnyx Edge Compute platform. This example demonstrates secure user authentication, token management, and role-based access control.

## Features

- **JWT Token Authentication** - Secure token-based authentication using HS256/RS256
- **Access & Refresh Tokens** - Dual token system with configurable expiration  
- **Role-Based Access Control** - Fine-grained permissions with user roles
- **Password Hashing** - Secure password storage with SHA-256 + salt
- **Token Refresh** - Seamless token renewal without re-authentication
- **Protected Endpoints** - Examples of secured API routes
- **Demo Users** - Pre-configured users for testing

## API Endpoints

| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/` | API information and demo users | ❌ | - |
| POST | `/auth/login` | Authenticate user and get tokens | ❌ | - |
| POST | `/auth/refresh` | Refresh access token | ❌ | - |
| POST | `/auth/logout` | Logout and invalidate tokens | ❌ | - |
| GET | `/auth/me` | Get current user information | ✅ | any |
| GET | `/protected` | Protected endpoint example | ✅ | any |
| GET | `/admin` | Admin-only endpoint | ✅ | admin |
| GET | `/users` | List all users | ✅ | admin |

## Demo Users

| Username | Password | Roles | Email |
|----------|----------|-------|-------|
| admin | admin123 | admin, user | admin@example.com |
| user1 | password123 | user | user1@example.com |
| demo | demo123 | user, demo | demo@example.com |

## Environment Variables

Configure JWT settings via environment variables:

```bash
# Generate a secure JWT secret (256-bit)
python3 -c 'import secrets; print("Generated JWT secret:", secrets.token_urlsafe(32))'
```

**Required Environment Variables:**
- `JWT_SECRET` - Secret key for signing tokens (strongly recommended for production)

**Optional Environment Variables:**
- `JWT_EXPIRY_MINUTES` - Access token expiration (default: 60 minutes)
- `JWT_REFRESH_EXPIRY_DAYS` - Refresh token expiration (default: 7 days)
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
```

## Usage Examples

### 1. User Login

```bash
# Login with demo user
curl -X POST https://your-function.dev.telnyxcompute.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Response:
```json
{
  "message": "Login successful",
  "user": {
    "user_id": "admin",
    "email": "admin@example.com",
    "roles": ["admin", "user"]
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "expires_at": "2024-01-01T13:00:00.000000"
}
```

### 2. Access Protected Endpoints

```bash
# Use access token in Authorization header
curl https://your-function.dev.telnyxcompute.com/protected \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 3. Get Current User Info

```bash
curl https://your-function.dev.telnyxcompute.com/auth/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 4. Refresh Access Token

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### 5. Admin-Only Endpoint

```bash
# Requires admin role
curl https://your-function.dev.telnyxcompute.com/admin \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 6. List Users (Admin)

```bash
curl https://your-function.dev.telnyxcompute.com/users \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 7. Logout

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

## Token Structure

### Access Token Payload
```json
{
  "user_id": "admin",
  "email": "admin@example.com", 
  "roles": ["admin", "user"],
  "iat": 1640995200,
  "exp": 1640998800,
  "type": "access"
}
```

### Refresh Token Payload
```json
{
  "user_id": "admin",
  "iat": 1640995200,
  "exp": 1641600000,
  "type": "refresh"
}
```

## Authentication Flow

1. **Login**: Send username/password to `/auth/login`
2. **Receive Tokens**: Get access token (short-lived) and refresh token (long-lived)
3. **API Calls**: Include access token in `Authorization: Bearer <token>` header
4. **Token Expiry**: When access token expires, use refresh token at `/auth/refresh`
5. **Logout**: Invalidate refresh token at `/auth/logout`

## Security Features

- **JWT Signature Verification** - All tokens cryptographically signed
- **Token Expiration** - Configurable short-lived access tokens
- **Role-Based Authorization** - Granular permission control
- **Password Hashing** - Secure password storage with salting
- **Refresh Token Rotation** - New refresh tokens issued on refresh
- **CORS Headers** - Cross-origin resource sharing support

## Development

### Local Testing

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
chmod +x test.sh
./test.sh
```

**Deployable on Telnyx Edge Compute**

## Production Considerations

- **JWT Secret**: Use a strong, random 256-bit secret key
- **Token Expiry**: Configure appropriate token lifetimes for your use case
- **User Storage**: Replace in-memory user storage with persistent database
- **Password Policy**: Implement strong password requirements
- **Rate Limiting**: Add rate limiting for authentication endpoints
- **HTTPS Only**: Ensure all communication uses HTTPS
- **Token Storage**: Secure client-side token storage

## Common Use Cases

- **API Authentication** - Secure REST API endpoints
- **Microservices Auth** - Service-to-service authentication
- **Single Sign-On (SSO)** - Centralized authentication service
- **Mobile App Auth** - Token-based mobile authentication
- **Admin Dashboards** - Role-based admin interfaces
- **B2B Integrations** - Partner API access control

## Error Handling

The service provides detailed error responses:
- `400`: Missing credentials or invalid request
- `401`: Invalid credentials or expired tokens
- `403`: Insufficient permissions for role-based endpoints
- `404`: User or endpoint not found
- `500`: Internal server errors

This example provides a solid foundation for implementing secure authentication and authorization in edge computing environments.