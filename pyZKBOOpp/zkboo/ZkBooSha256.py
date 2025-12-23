from ZkBooFunction import ZkBooFunction
from utils import FormatUtils, HashUtils, RandomUtils

from pysha256 import \
	sha256_plain, sha256_prove_commit, sha256_fake_proof, sha256_verify, \
	sha256_double_plain, sha256_double_prove_commit, sha256_double_fake_proof, sha256_double_verify, \
	sha256_input_xor_pub_plain, sha256_input_xor_pub_prove_commit, \
		sha256_input_xor_pub_fake_proof, sha256_input_xor_pub_verify

class Sha256Function(ZkBooFunction):
	def __init__(self, input_len_bytes):
		ZkBooFunction.__init__(self)
		self.func_plain        = sha256_plain
		self.func_prove_commit = sha256_prove_commit
		self.func_fake_proof   = sha256_fake_proof
		self.func_verify       = sha256_verify
		self.input_len_bytes1   = input_len_bytes

	def input_len_bytes(self):
		return self.input_len_bytes1


class Sha256InputXorPubFunction(ZkBooFunction):
	def __init__(self, input_len_bytes):
		ZkBooFunction.__init__(self)
		self.func_plain        = sha256_input_xor_pub_plain
		self.func_prove_commit = sha256_input_xor_pub_prove_commit
		self.func_fake_proof   = sha256_input_xor_pub_fake_proof
		self.func_verify       = sha256_input_xor_pub_verify
		self.input_len_bytes1  = input_len_bytes

	def input_len_bytes(self):
		return self.input_len_bytes1

def test_sha256():
	output_bytes = 32
	res = func_sha256.eval(input, output_bytes)
	print('sha256({}) = {}'.format(input, FormatUtils.dumpbin_to_readable(res)))

	res2 = func_sha256_inp_xor_pub.eval(input, output_bytes, inputpub)
	print('sha256({} ^ {}) = {}'.format(input, inputpub, FormatUtils.dumpbin_to_readable(res2)))


if __name__ == '__main__':
	input = '12345678'
	inputpub = '12341234'
	input_len_bytes = len(input)
	func_sha256 = Sha256Function(input_len_bytes)
	func_sha256_inp_xor_pub = Sha256InputXorPubFunction(input_len_bytes)

	test_sha256()



