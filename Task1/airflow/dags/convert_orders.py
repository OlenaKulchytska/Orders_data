from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import requests

def convert_orders():
    conn_src = psycopg2.connect(host='postgres-1', dbname='database1', user='user', password='password')
    conn_dst = psycopg2.connect(host='postgres-2', dbname='database2', user='user', password='password')
    cur_src = conn_src.cursor()
    cur_dst = conn_dst.cursor()
    
    response = requests.get('https://openexchangerates.org/api/latest.json?app_id=YOUR_APP_ID')
    rates = response.json().get('rates', {})
    
    cur_src.execute("SELECT order_id, customer_email, order_date, amount, currency FROM orders")
    orders = cur_src.fetchall()
    
    for order in orders:
        order_id, customer_email, order_date, amount, currency = order
        rate = rates.get(currency, 1)
        amount_eur = round(amount / rate, 2)
        cur_dst.execute("INSERT INTO orders_eur (order_id, customer_email, order_date, amount_eur, currency) VALUES (%s, %s, %s, %s, 'EUR')", (order_id, customer_email, order_date, amount_eur))
    
    conn_dst.commit()
    cur_src.close()
    conn_src.close()
    cur_dst.close()
    conn_dst.close()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('convert_orders', default_args=default_args, schedule_interval='0 * * * *')

task = PythonOperator(task_id='convert_orders_task', python_callable=convert_orders, dag=dag)