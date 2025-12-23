from pyzkboo_helper import pyzkboo_prove_response as __pyzkboo_prove_response, \
	get_MpcPartyView_input_offset as __get_MpcPartyView_input_offset, \
	pyzkboo_rounds as __pyzkboo_rounds, \
	pyzkboo_extract_es_from_Challenge as __pyzkboo_extract_es_from_Challenge, \
	pyzkboo_data_to_listbits as __pyzkboo_data_to_listbits, \
	pyzkboo_xor_data as __pyzkboo_xor_data, \
	pyzkboo_listbits_to_data as __pyzkboo_listbits_to_data



def pyzkboo_prove_response(zx_all, has32):
	return __pyzkboo_prove_response(zx_all, has32)

def get_MpcPartyView_input_offset():
	return __get_MpcPartyView_input_offset()

def pyzkboo_rounds():
	return __pyzkboo_rounds()

def pyzkboo_extract_es_from_Challenge(hash32):
	return __pyzkboo_extract_es_from_Challenge(hash32)

def pyzkboo_data_to_listbits(str):
	""" String representing a number is converted to the list of bits, significant bits have lower indices.

	:param str:
	:return: a list of bits
	"""
	return __pyzkboo_data_to_listbits(str)

def pyzkboo_xor_data(a, b):
	"""

	:param a: string
	:param b: string
	:return: string, the result of xor(a,b)
	"""
	return __pyzkboo_xor_data(a, b)

def pyzkboo_listbits_to_data(bits):
	""" Returns binary representation of the bits (should devide 8).

	:param bits: list of int bits
	:return: string,
	"""
	return __pyzkboo_listbits_to_data(bits)


print('pyzkboo #rounds = {}. (136 corresponds to 80 bit security)'.format(pyzkboo_rounds()))