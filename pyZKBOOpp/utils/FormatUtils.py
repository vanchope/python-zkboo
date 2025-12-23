def dumpbin_to_readable(bin_data):
	return ''.join(format(ord(ch), '02x') for ch in bin_data)


def string_to_int(st):
	""" max 8 bytes

	:param st:
	:return: the int number in little endian, i.e. ab = a + b<<8
	"""
	vals = map(ord, st)
	#assert len(st) <= 8 # why?
	res = 0
	for x in vals:
		res = (res << 8) + x
	return res
