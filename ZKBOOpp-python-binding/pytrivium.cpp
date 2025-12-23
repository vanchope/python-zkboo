#include <stdio.h>
#include "assert.h"

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "mpc_core.h"
#include "trivium/trivium.h"


#include "zkboo_helper.h"

namespace py = boost::python;

//typedef std::vector<std::string> VecStr;


//----------- definitions of `new' functions in ZKBoo format.

/* f(x1 || x2) = f(x1) ^ f(x2)
*/
template <typename T8, typename T32>
void trivium_double(const T8 input[],
		int input_len_bytes2, /*must be doubled, i.e. 20*/
		const uint8_t inputpub[], int inputpub_len_bytes,		
		T32 output[],
		int output_words){
	assert(input_len_bytes2 == 20);
	f32_double(input, input_len_bytes2, inputpub, inputpub_len_bytes, output, output_words, trivium);
}
int trivium_double_randomtape_len_bytes(int inputlen_bytes, int outputlen_bytes){
	return trivium_random_tape_len_in_bytes(inputlen_bytes, outputlen_bytes) * 2;
}


//  f(x ^ w) = y 
//  	where x, y are public,
//		w is private,
//      and |x| = |w|.
template <typename T8, typename T32>
void trivium_input_xor_pub(const T8 input[],
		int input_len_bytes, /*must be 10*/
		const uint8_t inputpub[], int inputpub_len_bytes,		
		T32 output[],
		int output_words){
	assert(input_len_bytes == 10);
	f32_input_xor_pub(input, input_len_bytes, inputpub, inputpub_len_bytes, output, output_words, trivium);
}
int trivium_input_xor_pub_randomtape_len_bytes(int inputlen_bytes, int outputlen_bytes){
	return trivium_random_tape_len_in_bytes(inputlen_bytes, outputlen_bytes);
}

// -------------------------------------------

const char * trivium_fname = "trivium";
const char * trivium_double_fname = "trivium_xor_trivium";
const char * trivium_input_xor_pub_fname = "trivium_input_xor_pub";


//FIXME zkboo_proof_commit
//https://stackoverflow.com/questions/6157409/stdvector-to-boostpythonlist
std::string trivium_plain(const std::string &input, int output_bytes){
	return zkboofunc_plain(input, "", output_bytes, trivium);
}
std::string trivium_double_plain(const std::string &input, int output_bytes){
	return zkboofunc_plain(input, "", output_bytes, trivium_double);
}
std::string trivium_input_xor_pub_plain(const std::string &input, const std::string &inputpub, int output_bytes){
	return zkboofunc_plain(input, inputpub, output_bytes, trivium_input_xor_pub);
}


py::tuple trivium_prove_commit(const std::string &input, const std::string &output){
	return pyzkboo_prove_commit(trivium_fname, input, "", output, trivium, trivium_random_tape_len_in_bytes);
}
py::tuple trivium_double_prove_commit(const std::string &input, const std::string &output){
	return pyzkboo_prove_commit(trivium_double_fname, input, "", output, trivium_double, trivium_double_randomtape_len_bytes);
}
py::tuple trivium_input_xor_pub_prove_commit(const std::string &input, const std::string &inputpub, const std::string &output){
	return pyzkboo_prove_commit(trivium_input_xor_pub_fname, input, inputpub, output, trivium_input_xor_pub, trivium_input_xor_pub_randomtape_len_bytes);
}



py::tuple trivium_fake_proof(int input_bytes_len, const std::string &output, const std::string &hash){	
	return pyzkboo_fake_proof(trivium_fname, input_bytes_len, "", output, hash, trivium, trivium_random_tape_len_in_bytes);
}
py::tuple trivium_double_fake_proof(int input_bytes_len, const std::string &output, const std::string &hash){	
	return pyzkboo_fake_proof(trivium_double_fname,input_bytes_len, "", output, hash, trivium_double, trivium_double_randomtape_len_bytes);
}
py::tuple trivium_input_xor_pub_fake_proof(int input_bytes_len, const std::string &inputpub, const std::string &output, const std::string &hash){	
	return pyzkboo_fake_proof(trivium_input_xor_pub_fname, input_bytes_len, inputpub, output, hash, trivium_input_xor_pub, trivium_input_xor_pub_randomtape_len_bytes);
}



bool trivium_verify(int input_bytes_len, const std::string &output_plain, const std::string &hash_v, const std::string &proof_commit, const py::list &z){
	return pyzkboo_verify(trivium_fname, input_bytes_len, "", output_plain, hash_v, proof_commit, z, trivium, trivium_random_tape_len_in_bytes);
}
bool trivium_double_verify(int input_bytes_len, const std::string &output_plain, 
		const std::string &hash_v, const std::string &proof_commit, const py::list &z){
	return pyzkboo_verify(trivium_double_fname, input_bytes_len, "", output_plain, hash_v, proof_commit, z, trivium_double, trivium_double_randomtape_len_bytes);
}
bool trivium_input_xor_pub_verify(int input_bytes_len, const std::string &inputpub, const std::string &output_plain, 
		const std::string &hash_v, const std::string &proof_commit, const py::list &z){
	return pyzkboo_verify(trivium_input_xor_pub_fname, input_bytes_len, inputpub, output_plain, hash_v, proof_commit, z, trivium_input_xor_pub, trivium_input_xor_pub_randomtape_len_bytes);
}



BOOST_PYTHON_MODULE(pytrivium)
{	
	py::def("trivium_plain", trivium_plain);
	py::def("trivium_prove_commit", trivium_prove_commit);
	py::def("trivium_fake_proof", trivium_fake_proof);	
	py::def("trivium_verify", trivium_verify);

	py::def("trivium_double_plain", trivium_double_plain);	
	py::def("trivium_double_prove_commit", trivium_double_prove_commit);
	py::def("trivium_double_fake_proof", trivium_double_fake_proof);
	py::def("trivium_double_verify", trivium_double_verify);

	py::def("trivium_input_xor_pub_plain", trivium_input_xor_pub_plain);
	py::def("trivium_input_xor_pub_prove_commit", trivium_input_xor_pub_prove_commit);
	py::def("trivium_input_xor_pub_fake_proof", trivium_input_xor_pub_fake_proof);	
	py::def("trivium_input_xor_pub_verify", trivium_input_xor_pub_verify);
}