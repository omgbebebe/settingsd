# -*- coding: utf-8 -*-

import socket
import os

from settingsd import const
from settingsd import config
from settingsd import service
from settingsd import shared
from settingsd import logger
from settingsd.tools.process import execProcess, SubprocessFailure
from os import path

##### Private constants #####
SERVICE_NAME = "ssl"
SSL_METHODS_NAMESPACE = "ssl"
CERTS_DIR = '/etc/opt/drweb.com/certs'
CERT_NAME = 'serv'
PEMFILE = path.join(CERTS_DIR, CERT_NAME + '.pem')
KEYFILE = path.join(CERTS_DIR, CERT_NAME + '.key')
CERTFILE = path.join(CERTS_DIR, CERT_NAME + '.crt')
CSRFILE = path.join(CERTS_DIR, CERT_NAME + '.csr')
CAFILE = path.join(CERTS_DIR, 'ca.crt')
CAKEY = path.join(CERTS_DIR, 'ca.key')
DAYS = 3650
CA_SUBJECT = '/C=RU/ST=1/L=1/O=1/OU=1/CN=1/emailAddress=1'
CERT_SUBJECT = '/C=RU/ST=1/L=1/O=1/OU=1/CN={}/emailAddress=1'


##### Private classes #####
class Ssl(service.FunctionObject) :	
	### DBus methods ###
	@service.functionMethod(SSL_METHODS_NAMESPACE)
	def generateCertificate(self):
		execProcess('openssl genrsa -out {} 2048'.format(CAKEY), shell=True)
		genca_cmd = 'openssl req -x509 -new -key {} -days {} -out {} -subj "{}"'.format(
			CAKEY, DAYS, CAFILE, CA_SUBJECT
		)
		execProcess(genca_cmd, shell=True)
		execProcess('openssl genrsa -out {} 2048'.format(KEYFILE), shell=True)
		gencsr_cmd = 'openssl req -new -key {} -out {} -subj {}'.format(
			KEYFILE, CSRFILE, CERT_SUBJECT.format(socket.gethostname())
		)
		execProcess(gencsr_cmd, shell=True)
		gencert_cmd = 'openssl x509 -req -in {} -CA {} -CAkey {} -CAcreateserial -out {} -days {}'.format(
			CSRFILE, CAFILE, CAKEY, CERTFILE, DAYS
		)
		execProcess(gencert_cmd, shell=True)

	@service.functionMethod(SSL_METHODS_NAMESPACE, in_signature="s", out_signature="b")
	def setCertificate(self, certificate):
		with open(PEMFILE, 'w+') as pem_file:
			pem_file.write(certificate)

		try:
			execProcess('openssl pkey -in {} -out {}'.format(PEMFILE, KEYFILE), shell=True)
			execProcess('openssl x509 -in {} -outform PEM -out {}'.format(PEMFILE, CERTFILE), shell=True)
			ca_cmd = 'openssl crl2pkcs7 -nocrl -certfile {} | openssl pkcs7 -print_certs -out {}'.format(
				PEMFILE, CAFILE
			)
			execProcess(ca_cmd, shell=True)
			return True
		except SubprocessFailure:
			return False


##### Public classes #####
class Service(service.Service) :
	### Public ###
	def initService(self) :
		shared.Functions.addSharedObject(SERVICE_NAME, Ssl(SERVICE_NAME, self))


	### Private ###
	@classmethod
	def serviceName(self) :
		return SERVICE_NAME
