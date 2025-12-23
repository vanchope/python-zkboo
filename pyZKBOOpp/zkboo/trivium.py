from ZkBooFunction import ZkBooFunction
import FormatUtils, HashUtils, RandomUtils
from pyzkboo_helper import pyzkboo_xor_data, pyzkboo_prove_response
from pytrivium import \
	trivium_plain, trivium_prove_commit, trivium_fake_proof, trivium_verify, \
	trivium_double_plain, trivium_double_prove_commit, trivium_double_fake_proof, trivium_double_verify, \
	trivium_input_xor_pub_plain, trivium_input_xor_pub_prove_commit, \
		trivium_input_xor_pub_fake_proof, trivium_input_xor_pub_verify

class TriviumFunction(ZkBooFunction):
	def __init__(self):
		ZkBooFunction.__init__(self)
		self.func_plain        = trivium_plain
		self.func_prove_commit = trivium_prove_commit
		self.func_fake_proof   = trivium_fake_proof
		self.func_verify       = trivium_verify

	def input_len_bytes(self):
		return 10


class TriviumDoubleFunction(ZkBooFunction):
	""" F(s1||s2) = F(s1) xor F(s2)

	"""
	def __init__(self):
		ZkBooFunction.__init__(self)
		self.func_plain        = trivium_double_plain
		self.func_prove_commit = trivium_double_prove_commit
		self.func_fake_proof   = trivium_double_fake_proof
		self.func_verify       = trivium_double_verify

	def input_len_bytes(self):
		return 2 * 10


class TriviumInputXorPub(ZkBooFunction):
	def __init__(self):
		ZkBooFunction.__init__(self)
		self.func_plain        = trivium_input_xor_pub_plain
		self.func_prove_commit = trivium_input_xor_pub_prove_commit
		self.func_fake_proof   = trivium_input_xor_pub_fake_proof
		self.func_verify       = trivium_input_xor_pub_verify

	def input_len_bytes(self):
		return 10

# ----------------------------------------------

def test_trivium():
	seed = '1234567890'
	output_bytes = 32
	res = func_trivium.eval(seed, output_bytes)
	print('trivium({}) = {}'.format(seed, FormatUtils.dumpbin_to_readable(res)))

def run_func_with_proof(fname, func, seed):
	output_bytes = 32
	output = func.eval(seed, output_bytes)
	proof_commitment, proof_all_parts = func.prove_commit(seed, output)
	print('[py] {}({}) = {}'.format(fname, seed, FormatUtils.dumpbin_to_readable(output)))
	print('proof commitment size = {}'.format(len(proof_commitment)))
	challenge = HashUtils.hash32bytes([output, proof_commitment])
	print('[challenge_p] = {}'.format(FormatUtils.dumpbin_to_readable(challenge)))
	proof_response_list = pyzkboo_prove_response(proof_all_parts, challenge)
	print('proof response len = {}'.format(len(proof_response_list)))
	print('proof response[0] = {}...'.format(FormatUtils.dumpbin_to_readable(str(proof_response_list[0])[:30])))
	proof = (proof_commitment, proof_response_list)

	# verify

	challenge_v = HashUtils.hash32bytes([output, proof[0]])
	print('[challenge_v] = {}'.format(FormatUtils.dumpbin_to_readable(challenge_v)))
	res = func.verify(output, challenge_v, proof[0], proof[1])
	print('[py] verified = {}'.format(res))
	assert(res)

	proof_list_modified = proof[1]
	proof_el_modified = list(proof_list_modified[1])
	print('test_wrong_proof: changed {} to {}'.format(ord(proof_el_modified[250]), ord('a')))
	proof_el_modified[250] = 'a'
	proof_list_modified[1] = ''.join(proof_el_modified)
	res = func.verify(output, challenge_v, proof[0], proof_list_modified)
	print('[py] verified wrong proof = {}'.format(res))
	assert(not res)

def test_trivium_with_proof():
	seed = '1234567890'
	run_func_with_proof("trivium", func_trivium, seed)


def test_trivium_fake_proof():
	seed = '1234567890'
	output_bytes = 32
	output = func_trivium.eval(seed, output_bytes)

	# fake proof
	hash = RandomUtils.random_as_string(32)
	proof_commit, proof_2parts = func_trivium.fake_proof(output, hash)

	#verify
	res = func_trivium.verify(output, hash, proof_commit, proof_2parts)
	assert(res)
	print('[py] fake proof trivium verified provided a challenge')


def test_trivium_double():
	seed1 = '1234567890'
	seed2 = '5566778899'
	seed12 = seed1 + seed2
	output_bytes = 32
	res = func_trivium_double.eval(seed12, output_bytes)
	print('trivium_double({}) = {}'.format(seed12, FormatUtils.dumpbin_to_readable(res)))
	y1 = func_trivium.eval(seed1, output_bytes)
	print('trivium({}) = {}'.format(seed1, FormatUtils.dumpbin_to_readable(y1)))
	y2 = func_trivium.eval(seed2, output_bytes)
	print('trivium({}) = {}'.format(seed2, FormatUtils.dumpbin_to_readable(y2)))
	y1_xor_y2 = pyzkboo_xor_data(y1, y2)
	print('xored = {}'.format(FormatUtils.dumpbin_to_readable(y1_xor_y2)))
	assert y1_xor_y2 == res

def test_trivium_double_with_proof():
	seed = '1234567890'+'5566778899'
	run_func_with_proof("trivium_double", func_trivium_double, seed)

def test_trivium_inp_xor_pub():
	x = '1234567890'
	w = '1111111111'
	output_bytes = 32
	res = func_trivium_inp_xor_pub.eval(input=w, output_len_bytes=output_bytes, inputpub=x)
	print('trivium("{}" ^ "{}") = {}'.format(x, w, FormatUtils.dumpbin_to_readable(res)))

	x_xor_w = pyzkboo_xor_data(x, w)
	res2 = func_trivium.eval(input=x_xor_w, output_len_bytes=output_bytes)
	print('trivium(= {} ) = {}'.format(FormatUtils.dumpbin_to_readable(x_xor_w), FormatUtils.dumpbin_to_readable(res2)))
	assert res == res2



if __name__ == '__main__':
	func_trivium = TriviumFunction()
	func_trivium_double = TriviumDoubleFunction()
	func_trivium_inp_xor_pub = TriviumInputXorPub()

	test_trivium()
	test_trivium_with_proof()
	test_trivium_fake_proof()

	test_trivium_double()
	test_trivium_double_with_proof()

	test_trivium_inp_xor_pub()
	print('test trivium done.')

'''
trivium(1234567890) = 15c589b3a253a6778797b883c2c4a27a6a375c759474f2b60c43975974ceed9b0182c10f768127e7
'''