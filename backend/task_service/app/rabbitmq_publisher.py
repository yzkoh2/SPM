import pika
import json
from flask import current_app


def publish_to_rabbitmq(queue_name, message):
    #Publish a message to RabbitMQ queue
    try:
        rabbitmq_url = current_app.config.get('RABBITMQ_URL', 'amqp://admin:admin123@rabbitmq:5672/')
        
        parameters = pika.URLParameters(rabbitmq_url)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        channel.queue_declare(queue=queue_name, durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error publishing to RabbitMQ: {e}")
        return False


def publish_status_update(task_id, old_status, new_status, changed_by_id):
    #Publish task status update to notification service
    message = {
        'task_id': task_id,
        'old_status': old_status,
        'new_status': new_status,
        'changed_by_id': changed_by_id
    }
    
    return publish_to_rabbitmq('task_status_updates', message)