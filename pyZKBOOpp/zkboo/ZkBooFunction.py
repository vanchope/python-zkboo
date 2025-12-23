
class ZkBooFunction:
	def __init__(self):
		self.func_plain = None
		self.func_prove_commit = None
		self.func_fake_proof = None
		self.func_verify = None

	def input_len_bytes(self):
		raise RuntimeError('not implemented in base class')

	def eval(self, input, output_len_bytes, inputpub=None):
		""" output the result of the PRG function given an input

		:param input:
		:param output_len_bytes:
		:param inputpub:
		:return:
		"""
		if inputpub is None:
			return self.func_plain(input, output_len_bytes)
		else:
			return self.func_plain(input, inputpub, output_len_bytes)

	def prove_commit(self, input, output, inputpub=None):  # FIXME check func output matches in c++
		"""

		:param input:
		:param output:
		:param inputpub:
		:return: a tuple ( proof_commit, proof_response as list)
		"""
		if inputpub is None:
			return self.func_prove_commit(input, output)
		else:
			return self.func_prove_commit(input, inputpub, output)

	def fake_proof(self, output, hash, inputpub=None):
		"""

		:param input_len_bytes:
		:param output:
		:param hash:
		:param inputpub:
		:return: a tuple (proof_commit, proof_committed_2parts as list)
		"""
		if inputpub is None:
			return self.func_fake_proof(self.input_len_bytes(), output, hash)
		else:
			return self.func_fake_proof(self.input_len_bytes(), inputpub, output, hash)

	def verify(self, output, challenge, proof_com, proof_resps, inputpub=None):
		"""

		:param output:
		:param challenge:
		:param proof_com:
		:param proof_resps:
		:param inputpub:
		:return: true if the proof verifies, otherwise false
		"""
		if inputpub is None:
			return self.func_verify(self.input_len_bytes(), output, challenge, proof_com, proof_resps)
		else:
			return self.func_verify(self.input_len_bytes(), inputpub, output, challenge, proof_com, proof_resps)
