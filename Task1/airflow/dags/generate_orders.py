from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import uuid
import random
import requests

def generate_orders():
    conn = psycopg2.connect(host='postgres-1', dbname='database1', user='user', password='password')
    cur = conn.cursor()
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD']
    
    for _ in range(5000):
        order_id = str(uuid.uuid4())
        customer_email = f'user{random.randint(1, 10000)}@example.com'
        order_date = datetime.utcnow() - timedelta(days=random.randint(0, 6))
        amount = round(random.uniform(10, 1000), 2)
        currency = random.choice(currencies)
        cur.execute("INSERT INTO orders (order_id, customer_email, order_date, amount, currency) VALUES (%s, %s, %s, %s, %s)", (order_id, customer_email, order_date, amount, currency))
    
    conn.commit()
    cur.close()
    conn.close()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('generate_orders', default_args=default_args, schedule_interval='*/10 * * * *')

task = PythonOperator(task_id='generate_orders_task', python_callable=generate_orders, dag=dag)