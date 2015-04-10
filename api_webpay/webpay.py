# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, g, request, redirect

from tbk.webpay.commerce import Commerce
from tbk.webpay.payment import Payment
from tbk.webpay.confirmation import Confirmation
from tbk.webpay.logging import configure_logger
from tbk.webpay.logging.official import WebpayOfficialHandler

from utils import *

import json
import os
import ast

LOG_BASE_PATH = os.path.join(os.path.dirname(__file__), "log")
configure_logger(WebpayOfficialHandler(LOG_BASE_PATH))

commerce = Commerce(testing=True)
#Pruebas Reales usar:
#commerce = Commerce.create_commerce()
webpay = Blueprint('webpay', __name__)


def initialize_app(app):
    app.register_blueprint(webpay)


# Genera un pago con transbank, se encarga de comunicarse y 
# entrega la url dada por transbank para redirigir al usuario.
@webpay.route("/webpay/payment", methods=["POST"])
@webpay.route("/webpay/payment/", methods=["POST"])
def payment():
    global commerce
    response = {'error': False}
    data = json.loads(request.data)
    try:
        b = Bill.objects.get(client_orden = data['orden'], 
                             amount = data['monto'], 
                             succ_url = data['succ_url'], 
                             fail_url = data['fail_url'])
    except:
        b = Bill(orden = make_orden(), 
                client_orden = data['orden'],
                session_id = data['sesion'], 
                amount = data['monto'], 
                ip = data['user_ip'], 
                state = State.objects.get(name = "Pendiente"), 
                succ_url = data['succ_url'], 
                fail_url = data['fail_url']
                )
        b.save() 

    finally:
        ip = current_app.config["BASE_IP"]
        url = current_app.config["BASE_URL"]
        payment = Payment(
            request_ip = data['user_ip'],
            commerce=commerce,
            success_url = 'http://' + url + '/webpay/success/',
            confirmation_url = 'http://' + ip + '/webpay/confirmation/',
            failure_url = 'http://' + url + '/webpay/failure/',
            session_id = data['sesion'],
            amount= data['monto'],
            order_id= b.orden,
        )
        response['url'] = payment.redirect_url
    return json.dumps(response)

# Transbank se comunica para confirmar la orden de compra.
# Esta es validada y en caso de estar todo bien se responde acknowledge
@webpay.route("/webpay/confirmation", methods=["POST"])
@webpay.route("/webpay/confirmation/", methods=["POST"])
def confirmation():
    global commerce
    confirmation = Confirmation(
        commerce=commerce,
        request_ip= request.remote_addr,
        data=request.form
    )
    bill = Bill.objects.get(orden = confirmation.order_id)
    if confirmation.is_success() and validation(confirmation, bill):
        bill.state = State.objects.get(name = "Aprobada")
        bill.message = confirmation.payload.message
        bill.auth_code = confirmation.payload.authorization_code
        bill.trx_id = confirmation.payload.transaction_id
        bill.trx_date = confirmation.payload.paid_at
        bill.last_digits = confirmation.payload.credit_card_last_digits
        bill.tipo_cuota = confirmation.payload.payment_type
        bill.num_cuota = confirmation.payload.installments
        bill.save()
        return commerce.acknowledge
    bill.state = State.objects.get(name = "Rechazada")
    bill.save()
    return commerce.reject


# Direccion ante compra exitosa.
# Manda por get el numero de la orden de compra
# esta se manda a la url de exito dada por la empresa
@webpay.route("/webpay/success", methods = ["POST"])
@webpay.route("/webpay/success/", methods = ["POST"])
def success():
    bill = Bill.objects.get(orden = request.form['TBK_ORDEN_COMPRA'])
    return redirect(bill.succ_url + "?orden=" + str(bill.client_orden))


# Direccion ante compra fallida.
# Manda por get el numero de la orden de compra
# esta se manda a la url de fallo dada por la empresa
@webpay.route("/webpay/failure", methods = ["POST"])
@webpay.route("/webpay/failure/", methods = ["POST"])
def failure():
    try:
        bill = Bill.objects.get(orden = request.form['TBK_ORDEN_COMPRA'])
    except:
        return json.dumps({'error': 'Transaccion no validada por transbank.'})
    return redirect(bill.fail_url + "?orden=" + str(bill.client_orden))


# URL de solicitud de informacion de una compra
# recibe por post una peticion de orden de compra
# y muestra la información respectiva
#Ejempĺo peticion: 
#r = requests.post('http://10.20.0.182:8000/webpay/bill', json={'orden':100001})
@webpay.route("/webpay/bill", methods=["POST"])
@webpay.route("/webpay/bill/", methods=["POST"])
def get_bill():
    data = json.loads(request.data)
    bill = Bill.objects.get(client_orden = data['orden'])
    return json.dumps(parse_bill(bill))


# URL de solicitud de informacion de una compra
# recibe por post una peticion de orden de compra
# y muestra la información respectiva
#Ejempĺo peticion: 
#r = requests.post('http://10.20.0.182:8000/webpay/bill', json={'orden':100001})
@webpay.route("/webpay/bills", methods=["POST"])
@webpay.route("/webpay/bills/", methods=["POST"])
def get_bills():
    data = json.loads(request.data)
    bills = []
    for orden in data['ordenes']:
        bill = Bill.objects.get(client_orden = orden)
        bills.append(parse_bill(bill))
    if len(data['ordenes'])==1:
        bills = bills[0]
    return json.dumps(bills)


@webpay.route("/webpay/query", methods=["POST"])
@webpay.route("/webpay/query/", methods=["POST"])
def query():
    kwargs = parse_kwargs(json.loads(request.data))
    if not kwargs:
        return json.dumps({})
    list_bill = parse_bills(Bill.objects(**kwargs))
    return json.dumps(list_bill)


@webpay.route("/webpay/test", methods=["GET"])
@webpay.route("/webpay/test/", methods=["GET"])
def test():
    from models import State
    return json.dumps(parse_bill(Bill.objects.get(orden = 200001)))
