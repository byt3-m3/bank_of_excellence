def create_dimension(name, value):
    return {
        'Name': name,
        'Value': value
    }


def update_metric(client, name_space, metric_name, dimensions, value=None, values=None):
    if value:
        return client.put_metric_data(
            Namespace=name_space,
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Dimensions': dimensions,
                    'Value': int(value)

                },
            ]
        )
