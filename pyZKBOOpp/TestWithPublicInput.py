from zkboo.ZkBooSha256 import Sha256Function, Sha256InputXorPubFunction
from utils import RandomUtils
from utils.timeutil import RunTimeMeasure, global_time1
from ZeroKnowledgeZKBOO import ZeroKnowledge


def test_function_with_public_input():
	""" added May 10, 2017.
	f(x^w)=y AND f(w)=y1,
	where x,y,y1 are public data,
	w is the secret
	"""

	secret_input = RandomUtils.random_as_string(bytes=100)  # 1000
	zkboo_form = 'f[w,x;y] AND f[w,x0;y1]'

	input_len_bytes = len(secret_input)
	print('Input length, bytes = {}'.format(input_len_bytes))

	zkboofunc = Sha256InputXorPubFunction(input_len_bytes)

	inputpub = RandomUtils.random_as_string(input_len_bytes)
	inputpub0 = '\0' * input_len_bytes
	output_len_bytes = 32
	priv = {'w': secret_input}
	publicdata = {'x': inputpub, 'x0': inputpub0,
				  'y': zkboofunc.eval(input=secret_input, output_len_bytes=output_len_bytes, inputpub=inputpub),
				  'y1': zkboofunc.eval(input=secret_input, output_len_bytes=output_len_bytes, inputpub=inputpub0)}

	print('public data: {}'.format(publicdata))  #FIXME better output

	timer_prove = RunTimeMeasure()
	zk = ZeroKnowledge(form=zkboo_form, zkboofunc=zkboofunc)
	proof = zk.prove(pub=publicdata, priv=priv)
	time_prove = timer_prove.stop()
	print('generated proof of size {} bytes'.format(len(proof)))
	print('Prove time = {} sec.'.format(time_prove))

	# Now comes the verify part. The verifier has all public data and a proof as string.

	timer_verify = RunTimeMeasure()
	zk_ver = ZeroKnowledge(form=zkboo_form, zkboofunc=zkboofunc)
	res = zk_ver.verify(pub=publicdata, proof=proof)
	time_verify = timer_verify.stop()
	print('verified : {} = {}'.format(zk.form, res))
	print('Verify time = {} sec.'.format(time_verify))


if __name__ == '__main__':
	global_time1.restart()
	try:
		test_function_with_public_input()
	finally:
		print('Total running time = {} sec.'.format(global_time1.stop()))
