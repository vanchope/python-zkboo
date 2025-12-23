#include <stdio.h>
#include "assert.h"

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "sha256.h"
#include "mpc_core.h"
#include "zkboo_helper.h"

namespace py = boost::python;

typedef std::vector<std::string> VecStr;


//----------- definitions of `new' functions in ZKBoo format.
template <typename T8, typename T32>
void sha256_double(const T8 input[],
		int input_len_bytes2, /*must be doubled, i.e. 20*/
		const uint8_t inputpub[], int inputpub_len_bytes,		
		T32 output[],
		int output_words){	
	f32_double(input, input_len_bytes2, inputpub, inputpub_len_bytes, output, output_words, sha256);
}
int sha256_double_randomtape_len_bytes(int inputlen_bytes, int outputlen_bytes){
	return sha256_random_tape_len_in_bytes(inputlen_bytes, outputlen_bytes) * 2;
}


template <typename T8, typename T32>
void sha256_input_xor_pub(const T8 input[],
		int input_len_bytes, /*must be 10*/
		const uint8_t inputpub[], int inputpub_len_bytes,		
		T32 output[],
		int output_words){
	f32_input_xor_pub(input, input_len_bytes, inputpub, inputpub_len_bytes, output, output_words, sha256);
}
int sha256_input_xor_pub_randomtape_len_bytes(int inputlen_bytes, int outputlen_bytes){
	return sha256_random_tape_len_in_bytes(inputlen_bytes, outputlen_bytes);
}



const char * sha256_fname = "sha256";
const char * sha256_double_fname = "sha256_xor_sha256";
const char * sha256_input_xor_pub_fname = "sha256_input_xor_pub";


//FIXME zkboo_proof_commit
//https://stackoverflow.com/questions/6157409/stdvector-to-boostpythonlist
std::string sha256_plain(const std::string &input, int output_bytes){
	return zkboofunc_plain(input, "", output_bytes, sha256);
}
std::string sha256_double_plain(const std::string &input, int output_bytes){
	return zkboofunc_plain(input, "", output_bytes, sha256_double);
}
std::string sha256_input_xor_pub_plain(const std::string &input, const std::string &inputpub, int output_bytes){
	return zkboofunc_plain(input, inputpub, output_bytes, sha256_input_xor_pub);
}


py::tuple sha256_prove_commit(const std::string &input, const std::string &output){
	return pyzkboo_prove_commit(sha256_fname, input, "", output, sha256, sha256_random_tape_len_in_bytes);
}
py::tuple sha256_double_prove_commit(const std::string &input, const std::string &output){
	return pyzkboo_prove_commit(sha256_double_fname, input, "", output, sha256_double, sha256_double_randomtape_len_bytes);
}
py::tuple sha256_input_xor_pub_prove_commit(const std::string &input, const std::string &inputpub, const std::string &output){
	return pyzkboo_prove_commit(sha256_input_xor_pub_fname, input, inputpub, output, sha256_input_xor_pub, sha256_input_xor_pub_randomtape_len_bytes);
}



py::tuple sha256_fake_proof(int input_bytes_len, const std::string &output, const std::string &hash){	
	return pyzkboo_fake_proof(sha256_fname, input_bytes_len, "", output, hash, sha256, sha256_random_tape_len_in_bytes);
}
py::tuple sha256_double_fake_proof(int input_bytes_len, const std::string &output, const std::string &hash){	
	return pyzkboo_fake_proof(sha256_double_fname,input_bytes_len, "", output, hash, sha256_double, sha256_double_randomtape_len_bytes);
}
py::tuple sha256_input_xor_pub_fake_proof(int input_bytes_len, const std::string &inputpub, const std::string &output, const std::string &hash){	
	return pyzkboo_fake_proof(sha256_input_xor_pub_fname, input_bytes_len, inputpub, output, hash, sha256_input_xor_pub, sha256_input_xor_pub_randomtape_len_bytes);
}



bool sha256_verify(
		int input_bytes_len, 
		const std::string &output_plain, 
		const std::string &hash_v, 
		const std::string &proof_commit, 
		const py::list &z){
	return pyzkboo_verify(sha256_fname, input_bytes_len, "", output_plain, hash_v, proof_commit, z, sha256, sha256_random_tape_len_in_bytes);
}
bool sha256_double_verify(
		int input_bytes_len, 
		const std::string &output_plain, 
		const std::string &hash_v, 
		const std::string &proof_commit, 
		const py::list &z){
	return pyzkboo_verify(sha256_double_fname, input_bytes_len, "", output_plain, hash_v, proof_commit, z, sha256_double, sha256_double_randomtape_len_bytes);
}
bool sha256_input_xor_pub_verify(
		int input_bytes_len, 
		const std::string &inputpub, 
		const std::string &output_plain, 
		const std::string &hash_v, 
		const std::string &proof_commit, 
		const py::list &z){
	return pyzkboo_verify(sha256_input_xor_pub_fname, input_bytes_len, inputpub, output_plain, hash_v, proof_commit, z, sha256_input_xor_pub, sha256_input_xor_pub_randomtape_len_bytes);
}



BOOST_PYTHON_MODULE(pysha256)
{	
	py::def("sha256_plain", sha256_plain);
	py::def("sha256_prove_commit", sha256_prove_commit);
	py::def("sha256_fake_proof", sha256_fake_proof);	
	py::def("sha256_verify", sha256_verify);

	py::def("sha256_double_plain", sha256_double_plain);	
	py::def("sha256_double_prove_commit", sha256_double_prove_commit);
	py::def("sha256_double_fake_proof", sha256_double_fake_proof);
	py::def("sha256_double_verify", sha256_double_verify);

	py::def("sha256_input_xor_pub_plain", sha256_input_xor_pub_plain);
	py::def("sha256_input_xor_pub_prove_commit", sha256_input_xor_pub_prove_commit);
	py::def("sha256_input_xor_pub_fake_proof", sha256_input_xor_pub_fake_proof);	
	py::def("sha256_input_xor_pub_verify", sha256_input_xor_pub_verify);
}