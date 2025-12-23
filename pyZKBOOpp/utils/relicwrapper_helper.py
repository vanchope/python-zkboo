import pyrelic


def Zr(num=-1, randomize=True, check_cache=True):
	"""

	:param num: If not specified, it will generate a random value
	:param check_cache:
	:return:
	"""
	if num == -1 and randomize:
		return __Zr(0).randomize()
	if check_cache and num >= 0 and num < ZR_CACHE_MAX:
		return zr[num]
	#return __Zr(num)
	return Zr_from_str(num)

def __Zr(num):
	return pyrelic.Zr(e, num)

def Zr_from_str(num):
	zr = __Zr(0)
	zr.fromString(str(num), 10)
	return zr

def Zr_type():
	return pyrelic.Zr

def G1(infinity=True):
	"""

	:param infinity:
	:return: G1 infinity point (~~identity) or random element
	"""
	return pyrelic.G1(infinity)


class RelicHlp:

	@staticmethod
	def zr_to_binstr(zr):
		return zr.toString(256)

	@staticmethod
	def zr_to_32byteLitEndian(x):
		""" Little-endian order is required for ZKBoo (extracting a challenge, where not all high order bits are used)

		:param x: Zr number = x_31 || x_30 || ... || x_0 as bytes
		:return: 256 bytes in Little-Endian, i.e. x_0 x_1 ... x_31
		"""
		return x.toString(int(256))[::-1]

	@staticmethod
	def zr_from_bin(data32bytes):
		e = Zr(0, check_cache=False)
		# Zr.fromBin takes only 32-byte inputs.
		e.fromBin(data32bytes)
		return e

	@staticmethod
	def zr_from_binstr(zr_str):
		a = Zr(num=0, randomize=False, check_cache=False)
		a.fromString(zr_str, 256)
		return a

	@staticmethod
	def g1_to_binstr(g1):
		return g1.toString(256)

	@staticmethod
	def g1_from_binstr(g1_str):
		g1 = G1(infinity=True)
		g1.fromString(g1_str, 256)
		return g1


def gen():
	"""
	:return: default generator of G1
	"""
	return e.get_g1_gen()


def randomG1():
	#return gen() ** Zr() # this is wrong
	return G1(infinity=False)


def get_identity_G1():
	return G1(infinity=True)


def close():
	pyrelic.delPairing()
	print('pympc: Closed pairing.')


pyrelic.initPairing()
e = pyrelic.Pairing()
zr = []
ZR_CACHE_MAX = 101
for i in range(ZR_CACHE_MAX):
	zr.append(__Zr(i))
easy_square = (zr[0] - zr[3]).mod2m(2) == zr[0]
easy_square_power = None
if easy_square:
	easy_square_power = (zr[0] - zr[3]) / zr[4] + zr[1]
print('relicwrapper_helper: Initialised pairing.')
print('relicwrapper_helper: G1 order = %s + 1' % str(zr[0] - zr[1]))
print('relicwrapper_helper: easy_square = '+str(easy_square))

inf = G1()
g1 = gen()
assert(g1 == inf * g1)


aa = [None] * 2

a = randomG1()
aa[0] = a
a = randomG1()
aa[1] = a
assert not aa[0] == aa[1]


def test_zr_G1_to_bin():
	a0 = Zr(0)
	a = Zr(5)
	st = RelicHlp.zr_to_binstr(a)
	a2 = RelicHlp.zr_from_binstr(st)
	assert(a == a2)
	a02 = Zr(0)
	assert(a0 == a02)

	g1 = G1(infinity=False)
	g1st = RelicHlp.g1_to_binstr(g1)
	g2 = RelicHlp.g1_from_binstr(g1st)
	assert(g1 == g2)

	print('test_zr_G1_to_bin passed.')

def test_zr_to_bin():
	x = Zr()
	x_bin = RelicHlp.zr_to_32byteLitEndian(x)
	print ('x={}'.format(x_bin))
	print(x % Zr(256))
	for i in range(len(x_bin)):
		print('x_bin [{}] = {}'.format(i, ord(x_bin[i])))

if __name__ == '__main__':
	try:
		test_zr_G1_to_bin()
	finally:
		close()
