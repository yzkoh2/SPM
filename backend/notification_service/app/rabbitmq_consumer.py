import pika
import json
import threading
import time
from flask import current_app
from . import service


class RabbitMQConsumer:
    #RabbitMQ Consumer for Notification Service
    def __init__(self, app):
        self.app = app
        self.connection = None
        self.channel = None
        self.rabbitmq_url = app.config['RABBITMQ_URL']
        
    def connect(self, max_retries=10, retry_delay=5):
        #Establish connection to RabbitMQ with retries
        for attempt in range(max_retries):
            try:
                print(f"🔌 Connecting to RabbitMQ (attempt {attempt + 1}/{max_retries})...")
                
                parameters = pika.URLParameters(self.rabbitmq_url)
                parameters.connection_attempts = 3
                parameters.retry_delay = 2
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                self.channel.queue_declare(queue='task_status_updates', durable=True)
                
                print("✅ Connected to RabbitMQ successfully")
                return True
                
            except pika.exceptions.AMQPConnectionError:
                if attempt < max_retries - 1:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Failed to connect after {max_retries} attempts")
                    return False
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return False
    
    def start_consuming(self):
        #Start consuming messages from the queue
        if not self.connection or self.connection.is_closed:
            if not self.connect():
                print("❌ Cannot start consumer - connection failed")
                return
        
        self.channel.basic_consume(
            queue='task_status_updates',
            on_message_callback=self.on_status_update_message,
            auto_ack=False
        )
        
        print("✅ RabbitMQ Consumer started. Waiting for messages...")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
            print("⏹️ Consumer stopped")
        except Exception as e:
            print(f"❌ Error in consumer: {e}")
    
    def on_status_update_message(self, channel, method, properties, body):
        #Handle incoming status update messages
        try:
            data = json.loads(body)
            
            with self.app.app_context():
                success = service.send_status_update_notification(
                    data['task_id'],
                    data['old_status'],
                    data['new_status'],
                    data['changed_by_id']
                )
                
                if success:
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def close(self):
        #Close RabbitMQ connection
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("⏹️ RabbitMQ connection closed")


def start_consumer_thread(app):
    #Start RabbitMQ consumer in a background thread
    consumer = RabbitMQConsumer(app)
    
    def run_consumer():
        print("⏳ Waiting for RabbitMQ to be ready...")
        time.sleep(10)
        consumer.start_consuming()
    
    thread = threading.Thread(target=run_consumer, daemon=True)
    thread.start()
    print("✅ RabbitMQ consumer thread started")
    
    return consumer