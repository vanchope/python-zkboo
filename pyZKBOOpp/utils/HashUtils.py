import hashlib
import random


def hash32bytes(hash_inputs):
	m = hashlib.sha256()
	for hash_input in hash_inputs:
		m.update(str(hash_input))
	dig = m.digest()
	return dig

# def hash32bytes(hash_inputs):
# 	# if DEBUG:
# 	# 	print('hash_inputs =\n\t' + '\n\t'.join([str(x) for x in hash_inputs]))
# 	res_int = hash_all(hash_inputs)
# 	return res_int


class KeyedHash:
	def __init__(self, moduli_bits):
		self.moduli_bits = moduli_bits
		self.mask = pow(2, moduli_bits) - 1
		self.regenerate_internal_key()

	def regenerate_internal_key(self):
		self.key = random.randint(1, pow(2, 64))

	# FIXME replace with SHA call
	def hash_all(self, hash_inputs):
		hash_inputs_sanitized = []
		hash_inputs_sanitized.append(self.key)
		hash_inputs_sanitized.extend(hash_inputs)
		res = hash32bytes(hash_inputs_sanitized)
		hash_value = 0
		for c in res:
			hash_value = (hash_value * 31 + ord(c)) & self.mask
		return hash_value


if __name__ == '__main__':
	data = [123]

	hashKeyed = KeyedHash(32)

	res = hashKeyed.hash_all(data)
	print(res)

	hashKeyed.regenerate_internal_key()
	res = hashKeyed.hash_all(data)
	print(res)
