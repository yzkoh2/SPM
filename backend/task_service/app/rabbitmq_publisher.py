import pika
import json
import time
from flask import current_app


def publish_to_rabbitmq(queue_name, message, max_retries=3, retry_delay=2):
    """
    Publish a message to RabbitMQ queue with retry logic.

    Args:
        queue_name: Name of the queue to publish to
        message: Message payload (will be JSON serialized)
        max_retries: Maximum number of connection retry attempts
        retry_delay: Initial delay between retries in seconds (uses exponential backoff)
    """
    for attempt in range(max_retries):
        try:
            rabbitmq_url = current_app.config.get('RABBITMQ_URL', 'amqp://admin:admin123@rabbitmq:5672/')

            parameters = pika.URLParameters(rabbitmq_url)
            parameters.connection_attempts = 3
            parameters.retry_delay = 2

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

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError) as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"⚠️  RabbitMQ connection failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                print(f"❌ Error publishing to RabbitMQ after {max_retries} attempts: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error publishing to RabbitMQ: {e}")
            return False

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

def publish_mention_alert(task_id, comment_id, mentioned_user_id, author_id, comment_body):
    #Publish mention alert message to RabbitMQ for notification service.
    message = {
        'task_id': task_id,
        'comment_id': comment_id,
        'mentioned_user_id': mentioned_user_id,
        'author_id': author_id,
        'comment_body': comment_body
    }
    
    success = publish_to_rabbitmq('mention_alerts', message)
    
    if success:
        print(f"✅ Mention alert published to RabbitMQ for user {mentioned_user_id}")
    else:
        print(f"❌ Failed to publish mention alert for user {mentioned_user_id}")
        
    return success