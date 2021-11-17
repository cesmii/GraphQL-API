import config

tank_name_prefix = config.tank_name_prefix
tanks_sizes = config.tanks_sizes

def mqtt_publish(value, topic, mqtt_client):
    #print (topic.capitalize() + " Value: " + str(value))
    mqtt_client.publish(topic, value)


def make_default_json(topic, tank_num):
    jsonobj={"tank_name": topic, "volume":0, "temperature":0, "size": tanks_sizes[tank_num]}
    return jsonobj