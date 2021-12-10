# -*- coding: utf-8 -*-

import json
from typing import Collection

from django.conf import settings
from opentelemetry.instrumentation import dbapi
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import Span, Status, StatusCode


def requests_callback(span: Span, response):
    """
    处理蓝鲸标准协议响应
    """
    try:
        json_result = response.json()
    except Exception:  # pylint: disable=broad-except
        return
    if not isinstance(json_result, dict):
        return
    result = json_result.get("result")
    if result is None:
        return
    span.set_attribute("result_code", json_result.get("code", 0))
    span.set_attribute("blueking_esb_request_id", json_result.get("request_id", ""))
    span.set_attribute("result_message", json_result.get("message", ""))
    span.set_attribute("result_errors", str(json_result.get("errors", "")))
    if result:
        span.set_status(Status(StatusCode.OK))
        return
    span.set_status(Status(StatusCode.ERROR))


def django_response_hook(span, request, response):
    """
    处理蓝鲸标准协议 Django 响应
    """
    if hasattr(response, "data"):
        result = response.data
    else:
        try:
            result = json.loads(response.content)
        except Exception:  # pylint: disable=broad-except
            return
    if not isinstance(result, dict):
        return
    span.set_attribute("result_code", result.get("code", 0))
    span.set_attribute("result_message", result.get("message", ""))
    span.set_attribute("result_errors", result.get("errors", ""))
    result = result.get("result", True)
    if result:
        span.set_status(Status(StatusCode.OK))
        return
    span.set_status(Status(StatusCode.ERROR))


class BKAppInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return []

    def _instrument(self, **kwargs):
        LoggingInstrumentor().instrument()
        RequestsInstrumentor().instrument(span_callback=requests_callback)
        DjangoInstrumentor().instrument(response_hook=django_response_hook)
        RedisInstrumentor().instrument()

        if getattr(settings, "IS_USE_CELERY", False):
            CeleryInstrumentor().instrument()

        if getattr(settings, "OTEL_INSTRUMENT_DB_API", False):
            import MySQLdb  # noqa

            dbapi.wrap_connect(
                __name__,
                MySQLdb,
                "connect",
                "mysql",
                {"database": "db", "port": "port", "host": "host", "user": "user"},
            )

    def _uninstrument(self, **kwargs):
        for instrumentor in self.instrumentors:
            instrumentor.uninstrument()
