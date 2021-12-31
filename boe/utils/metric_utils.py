from dataclasses import dataclass
from datetime import datetime
from typing import Union

from boe.env import STAGE
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate an API token from the "API Tokens Tab" in the UI
token = "Ewh6JxNbuiu_X2pDn-Xwbz3rYqPa0A51ljlJfaWsRGK2lFKdOlZvyIJeWhGV4ynTHoskeU0A1OBi-ctDsP9-sQ=="
org = "bits"
bucket = "boe_metrics"


# with InfluxDBClient(url="http://192.168.1.5:8086", token=token, org=org) as client:
#     write_api = client.write_api(write_options=SYNCHRONOUS)
#
#     point = Point("mem") \
#         .tag("host", "host1") \
#         .field("used_percent", 23.43234543) \
#         .time(datetime.utcnow(), WritePrecision.NS)
#
#     write_api.write(bucket, org, point)
#

@dataclass
class PlatformMetricTags:
    service_name: str


@dataclass
class PlatformMetricField:
    measurement: str
    value: Union[float, int]


class MetricWriter:

    def __init__(self):
        self.client = InfluxDBClient(url="http://192.168.1.5:8086", token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.org = 'bits'
        self.bucket = 'boe_metrics'

    def publish_metric(
            self,
            metric_name: str,
            tag_key: str,
            tag_value: str,
            field_name: str,
            field_value: float
    ):
        point = Point(metric_name) \
            .tag(tag_key, tag_value) \
            .field(field_name, field_value) \
            .tag('stage', STAGE) \
            .time(datetime.utcnow(), WritePrecision.NS)

        self.write_api.write(self.bucket, org, point)

    def publish_service_metric_v2(
            self,
            metric_name: str,
            tags: dict,
            fields: dict
    ):
        point = Point(metric_name)
        for key, val in tags.items():
            point.tag(key=key, value=val)

        for key, val in fields.items():
            point.field(field=key, value=val)

        point.time(datetime.utcnow(), WritePrecision.NS)

        self.write_api.write(self.bucket, org, point)

    def publish_service_metric(
            self,
            metric_name: str,
            field_name: str,
            field_value: Union[float, int],
            service_name: str
    ):
        self.publish_metric(
            metric_name=metric_name,
            field_name=field_name,
            field_value=float(field_value),
            tag_value=service_name,
            tag_key='ServiceName'
        )
