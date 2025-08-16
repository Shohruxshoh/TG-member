import json
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('json_logger')


class JsonRequestLogMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        # Logger sozlamalarini tekshirish
        logger.info("Middleware initialized - logger is ready")

    def process_request(self, request):
        request.start_time = time.time()
        if request.path.startswith('/api/'):
            logger.debug(f"Starting request for {request.path}")

    def process_response(self, request, response):
        if request.path.startswith('/api/'):
            log_data = {
                'timestamp': time.time(),
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'user': request.user.username if request.user.is_authenticated else None,
                'remote_addr': request.META.get('REMOTE_ADDR'),
                'response_size': len(response.content),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'processing_time': time.time() - getattr(request, 'start_time', 0)
            }

            if response.status_code >= 400:
                logger.error(json.dumps(log_data))
            else:
                logger.info(json.dumps(log_data))

        return response
