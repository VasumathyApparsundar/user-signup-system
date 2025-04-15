from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(conf)

def send_signup_event(email: str):
    producer.produce('user-signup', key="email", value=email)
    producer.flush()
