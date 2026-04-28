import os
import traceback
from typing import Any, Callable, Dict

from function.func import new


def mask_sensitive(env: Dict[str, str]) -> Dict[str, str]:
    """
    Mask sensitive environment variables when logging,
    but still pass the full environment to the function.
    """
    SENSITIVE_PREFIXES = (
        "AWS_",
        "SECRET_",
        "KEY_",
        "TOKEN_",
        "PASSWORD_",
    )

    masked = {}
    for key, value in env.items():
        if key.startswith(SENSITIVE_PREFIXES):
            masked[key] = "***MASKED***"
        else:
            masked[key] = value
    return masked


# Create instance
try:
    instance = new()
except Exception as e:
    print("❌ ERROR: Failed to create function instance via new()")
    traceback.print_exc()
    raise e

# Start the function with the FULL environment (no filtering)
if hasattr(instance, "start"):
    try:
        instance.start(dict(os.environ))
        # Safe logging without exposing secrets
        print("🔧 Function started with environment:", mask_sensitive(os.environ))
    except Exception as e:
        print("❌ ERROR: instance.start() failed")
        traceback.print_exc()
        raise e


async def app(scope: Dict[str, Any], receive: Callable, send: Callable):
    if scope["type"] != "http":
        await send({
            "type": "http.response.start",
            "status": 500,
            "headers": [(b"content-type", b"application/json")],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"error":"Only HTTP requests are supported"}',
        })
        return

    try:
        await instance.handle(scope, receive, send)
    except Exception:
        print("❌ ERROR: Exception while handling request")
        traceback.print_exc()
        await send({
            "type": "http.response.start",
            "status": 500,
            "headers": [(b"content-type", b"application/json")],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"error":"Internal server error","details":"See logs"}',
        })