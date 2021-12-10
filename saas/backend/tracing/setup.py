# -*- coding: utf-8 -*-

import os

from django.conf import settings
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import _KNOWN_SAMPLERS

from .instrumentor import BKAppInstrumentor


def setup_trace_config():
    environment = getattr(settings, "ENVIRONMENT", "dev")
    if environment == "dev":
        # local environment, use jaeger as trace service
        # docker run -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one
        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create(
                    {SERVICE_NAME: os.getenv("BKAPP_OTEL_SERVICE_NAME") or settings.OTEL_SERVICE_NAME}
                )
            )
        )
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost", agent_port=6831, udp_split_oversized_batches=True
        )
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
    else:
        trace.set_tracer_provider(
            tracer_provider=TracerProvider(
                resource=Resource.create(
                    {
                        "service.name": os.getenv("BKAPP_OTEL_SERVICE_NAME") or settings.OTEL_SERVICE_NAME,
                        "bk_data_id": int(os.getenv("BKAPP_OTEL_BK_DATA_ID")),
                    },
                ),
                sampler=_KNOWN_SAMPLERS[os.getenv("BKAPP_OTEL_SAMPLER", "parentbased_always_off")],
            )
        )
        otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("BKAPP_OTEL_GRPC_HOST"))
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)


def setup_by_settings():
    if getattr(settings, "ENABLE_OTEL_TRACE", False):
        setup_trace_config()
        BKAppInstrumentor().instrument()
