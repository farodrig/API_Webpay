from datetime import datetime, date
import unittest
import requests
import json
import webpay
import random

orden = 1

class TestWebpayFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_payment(self):
        global orden
        ############ Inicio variables del procedimiemto de almacenado#######
        orden = random.randint(0, 999999999999)
        dict = {'orden': orden
                'monto': 1000, 
                'sesion': 'ASDUIFWUGF', 
                'user_ip': '123.123.123.123', 
                'succ_url': 'http://localhost/webpay/success/',
                'fail_url': 'http://localhost/webpay/failure/'}
        ############ Fin variables del procedimiemto de almacenado#######
        r = requests.post('http://10.20.0.182:8000/webpay/payment/',json=dict)
        
        data = r.json()
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(data['url'])


    def test_bills(self):
        global orden
        ############ Inicio variables del procedimiemto de almacenado#######
        order = orden
        ############ Fin variables del procedimiemto de almacenado#######
        r = requests.post('http://10.20.0.182:8000/webpay/bills/', json={'ordenes': [order]})

        data = r.json()
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(data['orden'])


if __name__ == '__main__':
    unittest.main()
