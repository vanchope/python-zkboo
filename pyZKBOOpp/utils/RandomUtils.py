import os

from FormatUtils import dumpbin_to_readable, string_to_int

def random_as_string(bytes=1):
	res = os.urandom(bytes)
	return res

# -------------------------------

def test_rnd_bytes(bytes):
	print('\tTest {} random bytes'.format(bytes))
	rnd = random_as_string(bytes)
	print('as hex ->{}'.format(dumpbin_to_readable(rnd)))
	print('as int ->{}'.format(string_to_int(rnd)))

if __name__ == "__main__":
	test_rnd_bytes(1)
	test_rnd_bytes(2)
	test_rnd_bytes(4)
