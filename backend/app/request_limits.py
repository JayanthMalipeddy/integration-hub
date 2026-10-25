"""Bound actual ASGI request bytes, including requests without Content-Length."""
from starlette.responses import JSONResponse


class RequestLimitMiddleware:
    def __init__(self, app, limit=100000):
        self.app, self.limit = app, limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        lengths = [value for name, value in scope.get("headers", []) if name.lower() == b"content-length"]
        if lengths and (len(lengths) != 1 or not lengths[0].isdigit()):
            return await JSONResponse({"detail": "Invalid Content-Length"}, status_code=400)(scope, receive, send)
        if lengths and int(lengths[0]) > self.limit:
            return await JSONResponse({"detail": "Request exceeds 100 KB limit"}, status_code=413)(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > self.limit:
                return await JSONResponse({"detail": "Request exceeds 100 KB limit"}, status_code=413)(scope, receive, send)
            chunks.append(chunk)
            if not message.get("more_body", False):
                break
        supplied = False
        async def replay():
            nonlocal supplied
            if not supplied:
                supplied = True
                return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
            return await receive()
        await self.app(scope, replay, send)
