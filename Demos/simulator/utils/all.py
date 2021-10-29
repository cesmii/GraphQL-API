import config

tank_name_prefix = config.tank_name_prefix
tanks_sizes = config.tanks_sizes

def mqtt_publish(value, topic, mqtt_client):
    #print (topic.capitalize() + " Value: " + str(value))
    mqtt_client.publish(topic, value)

def make_default_json(topic, MAX_VOLUME, is_onetank):
    jsonobj={"tank_name": topic, "flowrate":0, "volume":0, "temperature":0, "size": MAX_VOLUME, "one_tank_model": int(is_onetank)}
    return jsonobj

def make_json_multitanks(topic, tank_num):
    jsonobj={"tank_name": topic, "volume":0, "temperature":0, "size": tanks_sizes[tank_num], "one_tank_model": 0}
    return jsonobj