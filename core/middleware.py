import json
import logging
import time
from typing import Dict, Any
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('secure_api_logger')


class JsonRequestLogMiddleware(MiddlewareMixin):
    """Faqat xato (500+) va exceptionlarni log qiluvchi middleware"""

    def __init__(self, get_response):
        super().__init__(get_response)
        self._init_logger()
        logger.info("Error-only API Logger initialized")

    def _init_logger(self):
        """Logger konfiguratsiyasini tekshirish"""
        if not logger.handlers:
            logger.addHandler(logging.StreamHandler())
            logger.warning("No handlers configured! Using fallback StreamHandler")

    def _sanitize_data(self, data: Any) -> Any:
        """Sezuvir ma'lumotlarni tozalash"""
        if isinstance(data, dict):
            return {k: self._sanitize_value(k, v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        return data

    def _sanitize_value(self, key: str, value: Any) -> Any:
        """Kalit bo'yicha sezuvir qiymatlarni maskalash"""
        sensitive_keys = ['token', 'password', 'secret', 'authorization', 'access', 'refresh']
        if any(s in key.lower() for s in sensitive_keys):
            return '*****FILTERED*****'
        return self._sanitize_data(value)

    def _get_request_data(self, request: HttpRequest) -> Dict[str, Any]:
        """So'rov ma'lumotlarini tozalangan holda olish"""
        try:
            # Birinchi marta o'qilganda cache qilib qo'yamiz
            if not hasattr(request, "_cached_body"):
                request._cached_body = request.body  # faqat bir marta o'qiladi

            raw_body = request._cached_body
            body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception as e:
            raw_body = getattr(request, "_cached_body", b"")
            body = {
                "parse_error": str(e),
                "raw_body": raw_body.decode(errors="ignore")[:200]
            }

        return {
            "method": request.method,
            "path": request.path,
            "query_params": self._sanitize_data(dict(request.GET)),
            "body": self._sanitize_data(body),
            "user": request.user.username if request.user.is_authenticated else None,
            "ip": self._get_client_ip(request),
        }

    def _get_response_data(self, response: HttpResponse, processing_time: float) -> Dict[str, Any]:
        """Javob ma'lumotlarini tozalangan holda olish"""
        try:
            content = json.loads(response.content.decode('utf-8')) if response.content else {}
        except Exception as e:
            content = {'parse_error': str(e), 'raw_content': str(response.content)[:200]}

        return {
            'status': response.status_code,
            'content': self._sanitize_data(content),
            'size_bytes': len(response.content) if response.content else 0,
            'processing_time_sec': round(processing_time, 4)
        }

    def _get_exception_data(self, exception: Exception) -> Dict[str, Any]:
        """Xato ma'lumotlarini yig'ish"""
        return {
            'type': exception.__class__.__name__,
            'message': str(exception),
            'args': [str(arg) for arg in getattr(exception, 'args', [])]
        }

    def process_exception(self, request: HttpRequest, exception: Exception):
        """500 xatoliklarini qayta ishlash"""
        if not request.path.startswith('/api/'):
            return None

        processing_time = time.time() - getattr(request, '_start_time', time.time())

        log_data = {
            'request': self._get_request_data(request),
            'exception': self._get_exception_data(exception),
            'processing_time': processing_time,
            'stack_trace': self._get_safe_traceback(exception),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        logger.error(json.dumps(log_data, indent=2, default=str))
        return None

    def _get_safe_traceback(self, exception: Exception) -> str:
        """Xavsiz stack trace olish"""
        try:
            import traceback
            return ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        except:
            return "Traceback not available"

    def process_request(self, request: HttpRequest):
        """So'rov vaqtini saqlash"""
        if request.path.startswith('/api/'):
            request._start_time = time.time()

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Faqat 500+ status codelarni log qilish"""
        if not request.path.startswith('/api/') or response.status_code < 500:
            return response

        processing_time = time.time() - getattr(request, '_start_time', time.time())
        log_data = {
            'request': self._get_request_data(request),
            'response': self._get_response_data(response, processing_time),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        logger.error(json.dumps(log_data, indent=2, default=str))
        return response

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Client IP manzilini olish"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR', '')

