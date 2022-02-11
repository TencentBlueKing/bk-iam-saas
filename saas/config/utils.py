import base64
import json
import logging
import os

from backend.common.local import local


def get_app_service_url(app_code: str) -> str:
    """
    使用app_code获取服务地址

    兼容环境变量配置与v3 smart的服务发现
    """
    if app_code == os.getenv("BKPAAS_APP_ID") and "BK_IAM_APP_URL" in os.environ:
        return os.environ["BK_IAM_APP_URL"]

    if app_code == "bk_itsm" and "BK_ITSM_APP_URL" in os.environ:
        return os.environ["BK_ITSM_APP_URL"]

    value = os.getenv("BKPAAS_SERVICE_ADDRESSES_BKSAAS")
    if not value:
        return ""

    decoded_value = json.loads(base64.b64decode(value).decode("utf-8"))
    return {item["key"]["bk_app_code"]: item["value"]["prod"] for item in decoded_value}.get(app_code, "")


def get_broker_url():
    if "RABBITMQ_HOST" in os.environ:
        return "amqp://{user}:{password}@{host}:{port}/{vhost}".format(
            user=os.getenv("RABBITMQ_USER"),
            password=os.getenv("RABBITMQ_PASSWORD"),
            host=os.getenv("RABBITMQ_HOST"),
            port=os.getenv("RABBITMQ_PORT"),
            vhost=os.getenv("RABBITMQ_VHOST"),
        )

    return os.getenv("BK_PAAS_HOST")


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = local.request_id
        return True
