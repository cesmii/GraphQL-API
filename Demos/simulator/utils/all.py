def mqtt_publish(value, topic, mqtt_client):
    #print (topic.capitalize() + " Value: " + str(value))
    mqtt_client.publish(topic, value)

def make_default_json(topic, MAX_VOLUME, is_onetank):
    jsonobj={"tank_name": topic, "flowrate":0, "volume":0, "temperature":0, "size": MAX_VOLUME, "one_tank_model": int(is_onetank)}
    return jsonobj