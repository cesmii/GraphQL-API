def mqtt_publish(value, topic, mqtt_client):
    print (topic.capitalize() + " Value: " + str(value))
    mqtt_client.publish(topic, value)
