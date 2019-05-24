import pywren_ibm_cloud as pywren
import random
import sys
import pika
import json



class callback_master:
	def __init__(self, num_maps):
		self.num_maps = num_maps
		self.num_peticions = 0
		self.num_permisos = 0
		self.peticions = []
	def __call__(self, channel, method, properties, body):
		body = body.decode('UTF-8')
		if(self.num_peticions < self.num_maps):
			self.peticions.append(body)
			self.num_peticions += 1
			if self.num_peticions is self.num_maps:
				channel.basic_publish(exchange='exchange_fanout', routing_key='', body='fi')
		elif self.num_peticions is self.num_maps:
			if(self.num_permisos == 0):
				num = random.randint(0,len(self.peticions)-1)
				channel.basic_publish(exchange='exchange_fanout', routing_key='', body='cua'+str(self.peticions[num]))
				self.peticions.remove(self.peticions[num])
				self.num_permisos += 1
			elif(body == 'fet'):
				num = random.randint(0,len(self.peticions)-1)
				channel.basic_publish(exchange='exchange_fanout', routing_key='', body='cua'+str(self.peticions[num]))
				self.peticions.remove(self.peticions[num])
				self.num_permisos += 1
			if self.num_permisos is self.num_maps:
				channel.stop_consuming()


class callback_mapper:
	def __init__(self, id_mapper, num_maps):
		self.id_mapper = str(id_mapper)
		self.num_maps = num_maps
		self.llista = []
		self.peticions = 0
	def __call__(self, channel, method, properties, body):
		body = body.decode('UTF-8')
		if (self.peticions == 0):
			if (body == 'fi'):
				self.peticions = 1
		else:
			if (body == 'cua'+ self.id_mapper):
				numero = random.randint(0,1000)
				channel.basic_publish(exchange='exchange_fanout', routing_key='', body=str(numero))
				channel.basic_publish(exchange='exchange_fanout', routing_key='', body='fet')
			elif ('cua' not in body and 'fet' not in body):
				self.llista.append(int(body))
			if (len(self.llista) == num_maps):
				channel.stop_consuming()
	def getLlista(self):
		return self.llista


def connectar():
	pw_config = json.loads(os.environ.get('PYWREN_CONFIG', ''))
	url = pw_config['rabbitmq']['amqp_url']
	params = pika.URLParameters(url)
	connection = pika.BlockingConnection(params)
	return connection


def my_function_master(num_maps):	
	connection = connectar()
	channel = connection.channel()
	
	#CREEM CUA I CALLBACK
	channel.queue_declare('master_queue')
	channel.queue_bind(exchange='exchange_fanout', queue='master_queue')
	callback = callback_master(num_maps)

	#LLEGIR PETICIONS I DONAR PERMISOS
	channel.basic_consume(callback, queue='master_queue', no_ack=True)
	channel.start_consuming()

	channel.queue_delete(queue='master_queue')
	connection.close()



def my_map_function(id_mapper, num_maps):
	connection = connectar()
	channel = connection.channel()
	
	#CREEM EXCHANGE FANOUT, CUA I CALLBACK
	callback = callback_mapper(str(id_mapper), num_maps)
	channel.exchange_declare(exchange='exchange_fanout', exchange_type='fanout')
	channel.queue_declare(str(id_mapper))
	channel.queue_bind(exchange='exchange_fanout', queue=str(id_mapper))
	
	#ENVIAR PETICIO A LA CUA MASTER
	channel.basic_publish(exchange='exchange_fanout', routing_key='', body=str(id_mapper))
	
	#ESPERAR PERMIS I ESCRIURE A LA CUA 
	channel.basic_consume(callback, queue=str(id_mapper), no_ack=True)
	channel.start_consuming()

	channel.queue_delete(queue=str(id_mapper))
	connection.close()
	return callback.getLlista()
	


if __name__ == '__main__':
	num_maps = int(sys.argv[1])
	args = []
	for num in range(num_maps):
		args.append({'id_mapper':num, 'num_maps':num_maps})

	pw = pywren.ibm_cf_executor(rabbitmq_monitor=True)
	pw.call_async(my_function_master, num_maps)
	pw2 = pywren.ibm_cf_executor(rabbitmq_monitor=True)
	pw2.map(my_map_function, args)	
	print(pw2.get_result())
	pw.clean()
	pw2.clean()

