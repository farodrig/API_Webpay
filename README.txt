
README api_webpay



Inicialización de la API:

	Para hacer funcionar la api deben instalarse los siguientes paquetes:
		- flask
		- flask-script
		- flask-mongoengine
		- tbk

	Esta instalación puede ser hecha a traves de pip o de forma manual.
	Para hacerlo con pip se puede llamar de la siguiente forma:
		$ pip install -r requirements.txt


	Se debe crear un archivo config.ini con las configuraciones de su sistema. Se recomienda utilizar config.ini.tmpl como base para la creación de config.ini. También se recomienda leer más abajo la sección de "Indicaciones config.ini" para un mejor entendimiento de como crearlo.

	Se debe tener instalado mongo y tenerlo corriendo en el sistema para que la API funcione correctamente.

	Para hacerlo correr, simplemente ejecute:
		$ python manage.py runserver



Indicaciones config.ini:

	- HOST: Debe ser 0.0.0.0 para que pueda ser vista desde afuera e interactuar con webpay.
	- PORT: Simplemente el puerto a utilizar, las llamadas deben ser redirigidas a ese puerto para que transbank se pueda conectar con la API.
	- BASE_IP: Debe ser la ip pública de la API, de modo de ser vista desde afuera por transbank, redirecciona a ubicación local del servidor. 
	- BASE_URL: URL pública de la aplicación.



Protocolo de comunicación de la API:

	1. El usuario de la API manda por método POST una consulta a la url de pago (por defecto PUBLIC_URL/webpay/payment) con la siguiente información:
		- 'orden': Número de orden de compra del carro. 
		- 'sesion': ID de sesion del comprador en la página del cliente de la API.
		- 'monto': Monto de la compra
		- 'user_ip': IP del comprador de la páginal del cliente de la API
		- 'succ_url': URL de éxito donde redirigir al usuario al haber una transacción exitosa.
		- 'fail_url': URL de fallo donde redirigir al usuario al haber una transacción fallida.
	

	2. La API con los datos proporcionados en el punto 1, manda una petición a transbank para que este entregue una url en caso de que la información proporcionada esté 	correcta. Esta información es entregada por parte de transbank a la API y esta es decodificada y entregada al usuario.

	3. El usuario recibe la URL por parte de la API y debe redireccionar al usuario a dicha URL.

	4. El usuario ingresa la información solicitada por transbank.

	5. Transbank verifica la información con la API, donde la API verifica que el monto sea el correcto, el número de orden sea el correcto, y que dicha orden no se 	   encuentre ya pagada. En caso de que todo este bien, entrega una confirmación a transbank, en caso contrario, la API rechaza.

	6. Transbank redirige a la página de éxito o rechazo de la API según corresponda. 

	7. La API redirige a la página de éxito o rechazo del cliente y pasa por método POST la orden de compra del producto.

	8.* Junto con esto, el cliente puede consultar a la API por la información relacionada por la compra de una orden de compra específica. Para esto se comunica por 		método POST con la API, mandando 'empresa' con el Nombre único de la empresa y 'orden' con el número de la orden de compra que desea solicitar.

	9.* La API retorna un diccionario con los siguientes datos:
		- 'orden': Orden de compra solicitado
		- 'sesion': ID de sesion del comprador
		- 'monto': Monto de la compra.
		- 'estado': Estado de la orden requerida.

		Si esta aprobada la compra tambien entrega los siguientes datos:
		- 'trx_id': ID de la transacción con transbank
		- 'trx_date': Fecha de la transacción en transbank
		- 'ult_digitos': 4 últimos digitos de la tarjeta de crédito.
		- 'tipo_cuota': Tipo de Cuotas solicitadas al momento de la compra.
		- 'num_cuota': Cantidad de cuotas solicitadas.

	* Relacionado con "Petición de información de una orden de compra"



Llamadas a la API:

	Petición de creación de pago con transbank:

		response = requests.post('http://ssb.synaptic.cl/webpay/payment/',json={'orden' : 3481, 'monto': 1000, 'sesion': 'ASDUFIENFASDF', 
			                        											'user_ip': '123.123.123.123', 'succ_url': 'http://ssb.synaptic.cl/webpay/success/',
			                        											'fail_url': 'http://ssb.synaptic.cl/webpay/failure/'})

	    if response.status_code == requests.codes.ok:
        	return redirect(response.json()['url']) #Respuesta con la url a direccionar el usuario
        return redirect('/pay/reject') #Pagina de rechazo											


    Petición de información de una orden de compra:
	
		response = requests.post('http://ssb.synaptic.cl/webpay/bill/', json={'orden' : 1235})
	    if response.status_code != requests.codes.ok:
	    	#Error
	    else:
	    	bill = response.json()


	Petición de información de varias ordenes de compra: * Si 'ordenes' es un arreglo de un solo elemento, responde una compra, no un arreglo de un elemento.
	
		response = requests.post('http://ssb.synaptic.cl/webpay/bills/', json={'ordenes' : [12365, 12341, 12345]})
	    if response.status_code != requests.codes.ok:
	    	bills = []
	    else:
	    	bills = response.json()
	    for bill in bills:
	    	print bill['orden']


	Petición de información de ordenes de compra filtrando por campos:
		
		Los campos permitidos para filtrar son:
			- 'fecha' : Debe ser escrito de la siguiente forma "22-01-1992" o 'dia-mes-año' siempre el año con todos sus números.
			- 'estado' : Puede ser 'Aprobada', 'Rechazada', 'Pendiente'
			- 'orden' : Debe ser un número entero positivo
			- 'monto' : Debe ser un número entero positivo
			- 'trx_id' : Debe ser un número entero positivo
			- 'sesion' : Debe ser un string

		Los campos que permiten rangos son:
			- 'fecha'
			- 'monto'
			- 'orden'
			- 'trx_id'

		Ejemplo de uso: 

			#Entrega todas las compras que fueron aprobadas
			response = requests.post('http://ssb.synaptic.cl/webpay/query/', json={'estado' : 'Aprobada'})

			#Entrega todas las compras con monto entre 1000 y 2000
			response = requests.post('http://ssb.synaptic.cl/webpay/query/', json={'monto' : {'min' : 1000, 'max' : 2000}})

			#Entrega todas las compras realizadas entre el 1 de Enero y el 10 de Febrero del 2015	
			response = requests.post('http://ssb.synaptic.cl/webpay/query/', json={'fecha' : {'min' : '1-1-2015', 'max' : '10-02-2015'}})
		    
		    if response.status_code != requests.codes.ok:
		    	bills = []
		    else:
		    	bills = response.json()
		    for bill in bills:
		    	# Los campos de bill son los mismos nombrados en el punto 9 del protocolo de comunicación.
		    	print bill['orden']


		Limitantes:

			- No permite más de un filtro por campo. Es decir, no se puede pedir todas las compras con monto 1000 o monto 2000.