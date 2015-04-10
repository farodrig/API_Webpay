from models import *
from datetime import datetime, timedelta


def initial():
    estados = ['Aprobada', 'Pendiente', 'Rechazada']
    for estado in estados:
        try:
            State.objects.get(name = estado)
        except:
            state = State(name = estado)
            state.save()


def make_orden():
    b = Bill.objects()
    if b.count():
        return b[b.count()-1].orden+1
    return Bill.orden.default


def validation(confirmation, bill):
    return confirmation.amount == bill.amount and bill.state.name != "Aprobada"


def parse_bill(bill):
    dict = {'orden': bill.client_orden,
            'sesion': bill.session_id,
            'monto': bill.amount,
            'estado': bill.state.name}
    if bill.state.name != "Aprobada":
        return dict
    dict.update({'auth_code': bill.auth_code,
            'trx_id': bill.trx_id,
            'trx_date': str(bill.trx_date),
            'ult_digitos': bill.last_digits,
            'tipo_cuota': bill.tipo_cuota,
            'num_cuota': bill.num_cuota})
    return dict


def parse_bills(bills):
    ans = []
    for bill in bills:
        ans.append(parse_bill(bill))
    return ans


def range_date(date, rango = 1):
    return [parse_date(date), parse_date(date, rango)]


def parse_date(date, delta_days = 0):
    fecha = datetime.strptime(date, "%d-%m-%Y")
    return fecha + timedelta(days = delta_days)


def parse_kwargs(data):
    kwargs = {}
    minmaxkeys = ['monto', 'orden', 'trx_id', 'fecha']
    keys = {'monto' : 'amount', 'fecha': 'trx_date', 'estado' : 'state', 'sesion': 'session_id', 'orden': 'client_orden', 'trx_id' : 'trx_id'}
    for key in data.keys():
        if isinstance(data[key], dict) and key in minmaxkeys:
            if key == "fecha":
                data[key]['max'] = parse_date(data[key]['max'])
                data[key]['min'] = parse_date(data[key]['min'])
            kwargs.update({keys[key] + "__lt": data[key]['max']})
            kwargs.update({keys[key] + "__gte": data[key]['min']})
        else:
            if key == "estado":
                kwargs.update({keys[key] : State.objects.get(name = data[key])})
            elif key == "fecha":
                dates = range_date(data[key])
                kwargs.update({keys[key] + "__lt": dates[1]})
                kwargs.update({keys[key] + "__gte": dates[0]})
            else:
                kwargs.update({keys[key] : data[key]})
    return kwargs
