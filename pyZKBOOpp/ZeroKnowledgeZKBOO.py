# Prepared on 27.08.2017
# Author: ivan

from parsimonious.grammar import Grammar

from utils.relicwrapper_helper import gen, Zr, Zr_from_str, G1, Zr_type, RelicHlp
from utils import HashUtils
import zkboo.pyzkboo_helper_wrapper as pyzkboo

from utils.timeutil import RunTimeMeasure, global_time1

DEBUG = False

OR = ' OR '
AND = ' AND '

# Example: form = 'a1=a2^x1*b2^r2'   order of operations: ^*=
grammar_equation = Grammar(r'''
	equation = lhs equals rhs
	lhs = identifier_g
	equals = '='
	rhs = product_group_elements
	product_group_elements = group_element (mul group_element)*
	group_element = identifier_g (power exp)?
	exp = identifier_zr
	identifier_g = letter_g+ (anychar)*
	identifier_zr = letter_zr+ (anychar)*
	power = '^'
	mul = '*'
	letter_g = 'a' / 'b' / 'c' / 'd' / 'g' / 'h' / 'p' / 'y'
	letter_zr = 'r' / 's' / 'x' / 'w' / 'v'
	digit = '0' / '1' / '2' / '3' / '4' / '5' / '6' / '7' / '8' / '9'
	anychar10 = 'a' / 'b' / 'c' / 'd' / 'e' / 'f' / 'g' / 'h' / 'i' / 'j'
	anychar20 = 'k' / 'l' / 'm' / 'n' / 'o' / 'p' / 'q' / 'r' / 's' / 't'
	anychar26 = 'u' / 'v' / 'w' / 'x' / 'y' / 'z'
	ANYCHAR4 = 'A' / 'B' / 'C' / 'D'
	anychar = digit / anychar10 / anychar20 / anychar26 / ANYCHAR4 / '_' / '.' / '$'
	''')


def zr_from_hash(hash_inputs):
	e = RelicHlp.zr_from_bin(HashUtils.hash32bytes(hash_inputs))
	e += Zr(0)  # to fix e>=mod issue
	return e


class ZKNode:
	def __init__(self):
		self.children = []
		self.parent = None
		self.can_be_proven = False
		self.should_be_proven = False
		self.challenge = None
		self.challenge_v = None  # For verifying (the root node)
		self.challenge_p = None  # Used to assign prover's challenges to nodes. Check: should be equal to challenge
		self.text = None

	def add_child(self, node):
		self.children.append(node)
		node.parent = self

	def check_prove_possible(self, zk):
		# zk has priv, pub as dicts
		return False

	def commit_to_using_free_challenge(self, zk):
		""" expected to be node's local computation. zk.challenge_inputs should be extended with new elements """
		raise RuntimeError('not implemented in base')

	def challenge_response(self, zk):
		""" depends on self.should_be_proven """
		raise RuntimeError('not implemented in base')

	def ver_prepare_challenge(self, zk):
		""" `verify' and update zk.challenge_inputs_v """
		raise RuntimeError('not implemented in base')

	def force_challenge(self, challenge_value):
		assert self.challenge is None or self.challenge==challenge_value
		self.challenge = challenge_value


class ZKNodeEquation(ZKNode):
	def __init__(self, text):
		ZKNode.__init__(self)
		self.text = text
		self.parsed = grammar_equation.parse(self.text)
		self.lhs, self.rhs = self.parsed.children[0].text, []
		self.dfs(self.parsed)
		self.rhs = self.rhs[1:]  # remove lhs
		self.exp_in_eq = set()
		for el in self.rhs:
			self.exp_in_eq.add(el[1])
		self.dupl_lhs = None
		self.responses = []
		self.dupl_lhs_v = None  # For verifying

	def dfs(self, node):
		if node.expr_name == 'identifier_g':
			self.rhs.append([node.text, 1])
		elif node.expr_name == 'identifier_zr':
			self.rhs[-1][1] = node.text
		for child in node.children:
			self.dfs(child)

	def check_prove_possible(self, zk):
		self.can_be_proven = True
		secrets_missing = []
		for exp in self.exp_in_eq:
			if exp not in zk.priv:
				self.can_be_proven = False
				secrets_missing.append(exp)
				if self.should_be_proven:
					raise RuntimeError('to prove it, private \'{}\' is required'.format(exp))
		if self.can_be_proven:
			rhs_eval = G1(infinity=True)
			for rhs_eq in self.rhs:
				if rhs_eq[1] == 1:
					rhs_eval *= zk.pub[rhs_eq[0]]
				else:
					rhs_eval *= zk.pub[rhs_eq[0]] ** zk.priv[rhs_eq[1]]
			self.can_be_proven = rhs_eval == zk.pub[self.lhs]
			# eval check is bad for performance, but it is easiest to implement # TODO optimize it?
		if zk.print_debug_messages:
			print('Node check proof: {} => {}, secrets missing: {}'.format(
				self.text, self.can_be_proven, secrets_missing))

	def commit_to_using_free_challenge(self, zk):
		# local computation; it depends on self.challenge (or equivalently on self.should_be_proven)
		# if it is NONE, then real prove will be used, otherwise fake proof
		self.dupl_lhs = G1()
		for group_el, exp in self.rhs:
			if exp not in zk.dupl_priv:
				zk.dupl_priv[exp] = Zr(randomize=True)
			self.dupl_lhs *= zk.pub[group_el] ** zk.dupl_priv[exp]
		if self.challenge is not None:  # fake challenge
			self.dupl_lhs *= zk.pub[self.lhs] ** self.challenge
		zk.challenge_inputs += [zk.pub[self.lhs], self.dupl_lhs]  # H ( ...lhs, lhs_dupl...)
		
	def challenge_response(self, zk):
		for el in self.rhs:
			k = el[1]
			resp = zk.dupl_priv[k]
			if self.should_be_proven:
				resp -= zk.priv[k] * self.challenge
			self.responses.append(resp)
		# FIXME at the moment, only exponents as variables (not constants) are supported
		# prepare answer
		zk.proof.append(self.challenge)
		zk.proof += self.responses

	def ver_prepare_challenge(self, zk):		
		self.challenge_p = zk.proof[zk.proof_idx]
		self.dupl_lhs_v = zk.pub_v[self.lhs] ** self.challenge_p
		zk.proof_idx += 1
		for el in self.rhs:
			self.dupl_lhs_v *= zk.pub_v[el[0]] ** zk.proof[zk.proof_idx]
			zk.proof_idx += 1
		zk.challenge_inputs_v += [zk.pub_v[self.lhs], self.dupl_lhs_v]

	def __repr__(self):
		return self.text


class ZKNodeOp(ZKNode):
	def __init__(self):
		ZKNode.__init__(self)
		self.children_proven = 0
		self.optype = None  # OR or AND
		self.first_child_proven = None
		self.sum_fake_challenges = Zr(0)

	def set_type(self, optype):
		if self.optype is None:
			self.optype = optype
		elif self.optype != optype:
			raise RuntimeError('types do not match')

	def check_prove_possible(self, zk):
		if self.optype == AND:
			self.can_be_proven = self.children_proven == len(self.children)
		else:  # OR
			self.can_be_proven = self.children_proven > 0
		if zk.print_debug_messages:
			print(' ==> ' + str(self.can_be_proven))

	def commit_to_using_free_challenge(self, zk):  # nothing to do
		pass

	def challenge_response(self, zk):  # nothing to do
		pass

	def ver_prepare_challenge(self, zk):
		pass

	# def __repr__(self):
	# 	return self.optype.join(['(' + str(child) + ')' for child in self.children])


class ZKBooNode(ZKNode):
	def __init__(self, text, function):
		""" f[x,y] denotes a ZKBooNode

		:param text:
		:param function: ZKBoo function
		:return:
		"""
		# f(input,publicdata)
		# convention is that the names are [A-Z]+[0-9]*
		ZKNode.__init__(self)
		self.text = text
		self.input, self.inputpub, self.output = ZKBooNode.parse_F_text(text)

		self.function = function

		self.es = None
		# runtime variables while proving
		self.proof_commit = None
		self.proof_3resp = None
		self.proof_2resp = None
		# verify
		self.proof_commit_p = None
		self.proof_2resp_p = None


	@staticmethod
	def parse_F_text(text):
		""" f[x;y] or f[x,xpub;y]

		:param text:
		:return:
		"""
		assert (text[0:2]=='f['), 'received text: {}'.format(text)
		assert text[-1]==']'
		semicol = text.index(';')  # raise Ex if not found
		input_part = text[2:semicol]
		if ',' in input_part:
			comma = input_part.index(',')
			input = input_part[:comma]
			inputpub = input_part[comma+1:]
		else:
			input = input_part
			inputpub = None
		output = text[semicol + 1:-1]  # public
		return input, inputpub, output

	@staticmethod
	def is_ZKBooNode(text):
		"""

		:param text:
		:return:  true if text starts with 'f'
		"""
		return text[0] == 'f'

	def prepare_and_get_inputpub(self, pub):
		return None if self.inputpub is None else pub[self.inputpub]

	def check_prove_possible(self, zk):
		if zk.priv is None or self.input not in zk.priv or self.output not in zk.pub:
			self.can_be_proven = False
		else:
			# check that plain output is correct
			self.can_be_proven = self.function.eval(
				zk.priv[self.input], len(zk.pub[self.output]), self.prepare_and_get_inputpub(zk.pub)
			) == zk.pub[self.output]

		if self.can_be_proven:  #if self.should_be_proven:
			self.proof_commit, self.proof_3resp = self.function.prove_commit(
				zk.priv[self.input], zk.pub[self.output], self.prepare_and_get_inputpub(zk.pub))


	def commit_to_using_free_challenge(self, zk):
		if not self.should_be_proven: # fake proof
			# check whether providing 3resp is compatible instead of running fake_proof
			assert self.challenge is not None
			self.proof_commit, self.proof_2resp = self.function.fake_proof(
				zk.pub[self.output], RelicHlp.zr_to_32byteLitEndian(self.challenge),
				self.prepare_and_get_inputpub(zk.pub))
		zk.challenge_inputs += [self.proof_commit]

	def challenge_response(self, zk):
		if self.proof_2resp is None:  # it was previously proven
			self.proof_2resp = pyzkboo.pyzkboo_prove_response(self.proof_3resp, RelicHlp.zr_to_32byteLitEndian(self.challenge))
		zk.proof += [self.challenge, self.proof_commit, self.proof_2resp]
		#add opening information for 2 out of 3 commitments for each round

	def ver_prepare_challenge(self, zk):
		self.challenge_p = zk.proof[zk.proof_idx]
		zk.proof_idx += 1
		self.proof_commit_p = zk.proof[zk.proof_idx]
		zk.proof_idx += 1
		self.proof_2resp_p = zk.proof[zk.proof_idx]
		zk.proof_idx += 1

		res = self.function.verify(
			zk.pub_v[self.output],
			RelicHlp.zr_to_32byteLitEndian(self.challenge_p),
			self.proof_commit_p,
			self.proof_2resp_p,
			inputpub=self.prepare_and_get_inputpub(zk.pub_v))
		if not res:
			raise RuntimeError('proof failed')
		zk.challenge_inputs_v += [self.proof_commit_p]


class ZeroKnowledge:
	""" The class has `one-time' methods prove/verify. The model is symbolic, data are provided via pub/priv dicts.

	All 'rhs' identifiers become part of hash H.
	All secrets are randomly duplicated in the proof.
	Let (e, s) be the proof, where e is a hash. Then, |s| = #secrets.

	Example: (a,b,a_bar) are of form (g^k, c_p^k, g_bar^k)

	See \cite{Shoup'98,Securing Threshold Cryptosystems against CCA},
	\cite{Camenisch'97,Proof Systems for General Statements about Discrete Logarithms}

	Nodes with ZKBoo functions are supported.
	"""
	def __init__(self, form, zkboofunc=None):
		self.zkboofunc = zkboofunc
		self.pub = None
		self.priv = None
		self.pub_v = None
		self.proof = None
		self.form = form
		self.root = None
		if self.form is not None:
			self.parse_manually(self.form)  # otherwise add nodes manually
		self.dupl_priv = None
		self.challenge_inputs = None
		# For proofs
		self.challenge_inputs_v = []
		self.proof_idx = None
		self.print_debug_messages = False

	def print_form(self):
		raise RuntimeError('not implemented')

	def set_priv(self, priv):
		self.priv = priv

	def set_pub(self, pub):
		self.pub = pub

	def create_token(self, st):
		"""it can be either ZKNodeEquation, or
		f(...) --> ZKBooNode

		:param st:
		:return:
		"""
		if ZKBooNode.is_ZKBooNode(st):
			zkboo_node = ZKBooNode(st, self.zkboofunc)
			node = ZKNodeOp()
			node.set_type(AND)
			node.add_child(zkboo_node)
			return node
		else:
			# ok, it's an equation
			eq = ZKNodeEquation(st)
			return eq

	def add_token(self, begin, end, node, form):
		if begin >= 0:  # if begin==-1, then there was no token
			eq = self.create_token(form[begin:end])
			node.add_child(eq)

	def parse_manually(self, form, start_node=None):
		if start_node is None:
			self.root = ZKNodeOp()
			start_node = self.root
		node_cur = start_node
		token_started = -1
		i = 0
		while i < len(form):
			node_next = node_cur
			if form[i] == '(':
				node_new = ZKNodeOp()
				node_cur.add_child(node_new)
				node_next = node_new
			elif form[i] == ')':
				self.add_token(token_started, i, node_cur, form)
				token_started = -1
				if node_cur.optype is None:
					node_cur.optype = AND  # instead of normalizing, we simply assume it is an AND node
				node_next = node_cur.parent
			elif form[i] == ' ':
				self.add_token(token_started, i, node_cur, form)
				token_started = -1
				if form[i:i+len(OR)] == OR:
					node_cur.set_type(OR)
					i += len(OR)-1
				elif form[i:i+len(AND)] == AND:
					node_cur.set_type(AND)
					i += len(AND)-1
				else:
					raise RuntimeError()
			else:  # letters or digits
				if token_started < 0:
					token_started = i
			i += 1
			node_cur = node_next
		if token_started >= 0:
			self.add_token(token_started, len(form), node_cur, form)
		# normalize the tree?

	def prove(self, pub, priv):
		""" pub is assigned to self.pub, same holds for priv.

		:param pub:
		:param priv:
		:return: proof as a list
		"""
		self.set_pub(pub)
		self.set_priv(priv)
		self.dupl_priv = {}
		self.challenge_inputs = []

		# sets node.first_child_proven for OR-nodes; sets node.can_be_proven
		self.dfs(self.root, post=self.post_prove_check)
		self.dfs(self.root, pre=self.pre_decide_prove)  # decides what should be proven
		if not self.root.can_be_proven:
			raise RuntimeError('proof not possible')
		self.dfs(self.root, pre=self.pre_assign_fake_challenge)

		self.dfs(self.root, pre=self.zk_commit_to_using_fake_challenge)  # fill in self.challenge_inputs for ROM
		# TODO add public constants to hash inputs, e.g. group generator etc
		self.root.force_challenge(zr_from_hash(self.challenge_inputs))
		#print('prove: root challenge is {}'.format(self.root.challenge))
		self.dfs(self.root, pre=self.pre_fill_missing_challenge)
		self.proof = []
		# prepare response depending on the challenge assigned to the node
		self.dfs(self.root, pre=self.zk_challenge_response)
		return ProofSerializer().convert_proof_to_str(self.proof)

	def dfs(self, tree, pre=None, post=None):
		if pre is not None:
			pre(tree)
		for child in tree.children:
			self.dfs(child, pre, post)
		if post is not None:
			post(tree)

	def post_prove_check(self, node):
		node.check_prove_possible(self)  # sets node.can_be_proven
		if node.can_be_proven and node.parent is not None:
			assert isinstance(node.parent, ZKNodeOp)
			node.parent.children_proven += 1
			if node.parent.first_child_proven is None:
				node.parent.first_child_proven = node

	@staticmethod
	def pre_decide_prove(node):
		if node.parent is None:  # it is root
			node.should_be_proven = True
			return
		# node.parent is always ZKNodeOp
		if not node.parent.should_be_proven:
			node.should_be_proven = False
			return
		# should be proven!
		if node.parent.optype == OR:
			node.should_be_proven = (node.parent.first_child_proven is node)
		else:
			node.should_be_proven = node.parent.should_be_proven

	@staticmethod
	def pre_assign_fake_challenge(node):
		if not node.should_be_proven:  # it is definitely not the root node
			assert node.challenge is None
			if node.parent.optype == OR:
				if not node.parent.should_be_proven and node.parent.children[len(node.parent.children)-1] is node:
					node.force_challenge(node.parent.challenge - node.parent.sum_fake_challenges)
				else:
					node.force_challenge(Zr(randomize=True))
				node.parent.sum_fake_challenges += node.challenge
				# sum_fake_challenges should be equal to challenge if the node should not be proven!
			else:  # AND
				node.force_challenge(node.parent.challenge)

	def zk_commit_to_using_fake_challenge(self, node):
		node.commit_to_using_free_challenge(self)

	def zk_submit_inputs_for_ROM(self, node):
		node.submit_inputs_for_ROM(self)

	@staticmethod
	def pre_fill_missing_challenge(node):
		if node.challenge is None:  # root is excluded, so node.parent is not None
			if node.should_be_proven:
				node.challenge = node.parent.challenge - node.parent.sum_fake_challenges
			else:
				raise RuntimeError()
			# corner case: no proof is required

	def zk_challenge_response(self, node):
		node.challenge_response(self)

	# ----- VERIFY ----------
	def verify(self, pub, proof):
		self.pub_v = pub
		self.proof = ProofSerializer().convert_str_to_proof(proof)
		self.proof_idx = 0

		self.dfs(self.root, pre=self.zkver_prepare_challenge)
		assert self.proof_idx == len(self.proof)  # all proof elements have been consumed by dfs

		self.root.challenge_v = zr_from_hash(self.challenge_inputs_v)
		#print('verify: root challenge is {}'.format(self.root.challenge_v))
		self.dfs(self.root, post=self.ver_post_verify_challenge)
		result = self.root.challenge_p == self.root.challenge_v
		return result

	def zkver_prepare_challenge(self, node):
		node.ver_prepare_challenge(self)

	@staticmethod
	def ver_post_verify_challenge(node):
		if node.parent is not None:
			if node.parent.optype == OR:
				if node.parent.challenge_p is None:
					node.parent.challenge_p = Zr(0)
				node.parent.challenge_p += node.challenge_p
			else:  # node.parent = AND
				if node.parent.challenge_p is None:
					node.parent.challenge_p = node.challenge_p
				else:
					assert node.parent.challenge_p == node.challenge_p


class ZKCompiler:
	def __init__(self):
		pass

	@staticmethod
	def or_statements(stmts):
		return ' OR '.join(['({})'.format(stmt) for stmt in stmts])

	@staticmethod
	def and_statements(stmts):
		return ' AND '.join(['({})'.format(stmt) for stmt in stmts])

class ProofSerializer:
	""" One-time proof serializer
	"""

	def __init__(self):
		self.output_list = []
		# for deserialize
		self.st = None
		self.index = 0

	def convert_proof_to_str(self, proof):
		self.__serialize(proof)
		return ''.join(self.output_list)

	def convert_str_to_proof(self, str_proof):
		return self.__deserialize(str_proof)

	def __append_str(self, st):
		self.output_list.append(str(len(st)))
		self.output_list.append(':')
		self.output_list.append(st)

	def __serialize(self, data):
		if isinstance(data, list):
			self.output_list.append('L')
			for part in data:
				self.__serialize(part)
			self.output_list.append('E')
		elif isinstance(data, str):
			self.output_list.append('S')
			self.__append_str(data)
		elif isinstance(data, Zr_type()):
			self.output_list.append('Z')
			zr_str = str(data)
			self.__append_str(zr_str)
		else:
			raise RuntimeError("unexpected instanse type : {}".format(type(data)))

	def __deserialize(self, st):
		self.st = st
		self.index = 0
		return self.__parse_string_token()

	def __parse_string_token(self):
		token_type = self.st[self.index]
		self.index += 1
		if token_type == 'L':
			list_tokens = []
			while self.st[self.index] != 'E':
				list_tokens.append(self.__parse_string_token())
			self.index += 1
			return list_tokens
		elif token_type in 'SZ':  # S or Z
			# read length
			end = self.index + 1
			while self.st[end] != ':':
				end += 1
			str_len = int(self.st[self.index: end])
			self.index = end + 1
			token = self.st[self.index: self.index + str_len]
			self.index += str_len
			if token_type == 'S':
				return token
			assert token_type == 'Z'
			zr = Zr_from_str(token)
			return zr
		else:
			raise RuntimeError('unexpected token type: {}'.format(token_type))


# ---------------------------- TESTS -----------------------

def test_old():
	zk = ZeroKnowledge(form='y=g^x')
	g = gen()
	x = Zr()
	y = g ** x
	pub = {'g':g, 'y':y}
	priv = {'x':x}
	proof = zk.prove(pub, priv)
	print('Proof: '+str(proof))
	res = zk.verify(pub, proof)
	assert res, 'ZK verification failed'
	print('ZK verified for %s' % zk.form)


def run_zk(zk_form, zkboofunc, publicdata, priv):
	"""

	:param zk_form:
	:param zkboofunc:
	:param publicdata:
	:param priv:
	:return:
	"""
	zk = ZeroKnowledge(form=zk_form, zkboofunc=zkboofunc)
	proof = zk.prove(pub=publicdata, priv=priv)

	# proof and zk.pub are used in verify

	zk_v = ZeroKnowledge(form=zk_form, zkboofunc=zkboofunc)
	res = zk_v.verify(pub=zk.pub, proof=proof)
	print('verified : {} = {}'.format(zk_v.form, res))
	return res


# ------------------------------------------------

def test_parenthesis():
	g = gen()
	x = Zr()
	y = g ** x
	y2 = g ** Zr()
	pub = {'g':g, 'y':y, 'y2':y2}
	priv = {'x':x}

	assert run_zk('y=g^x', None, pub, priv)
	assert run_zk('(y=g^x)', None, pub, priv)
	assert run_zk('((y=g^x))', None, pub, priv)
	assert run_zk('y=g^x OR y2=g^x', None, pub, priv)
	assert run_zk('(y=g^x) OR (y2=g^x)', None, pub, priv)
	assert run_zk('((y=g^x) OR (y2=g^x))', None, pub, priv)


def test_serializer():
	proof = ['a', ['b', 'c'], 'd', ['e', 'f']]
	proof_str = ProofSerializer().convert_proof_to_str(proof)
	proof_ver = ProofSerializer().convert_str_to_proof(proof_str)
	assert len(proof) == len(proof_ver)
	# print('test_serializer: please check the rest manually')


if __name__ == '__main__':
	# time1 = RunTimeMeasure()
	global_time1.restart()

	try:
		test_parenthesis()
		test_serializer()
	finally:
		print('Total running time = {} sec.'.format(global_time1.stop()))
