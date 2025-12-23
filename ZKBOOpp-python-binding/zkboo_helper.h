#ifndef ZKBOO_HELPER_H_
#define ZKBOO_HELPER_H_

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "mpc_core.h"

namespace py = boost::python;

typedef std::vector<std::string> VecStr;

//----------- definitions of some functions in ZKBoo format.

/* f(x1 || x2) = f(x1) ^ f(x2)
*/
template <typename T8, typename T32>
void f32_double(const T8 input[],
		int input_len_bytes2, /*must be doubled, i.e. 20*/
		const uint8_t inputpub[], int inputpub_len_bytes,		
		T32 output[],
		int output_words,
		void (*func32)(const T8 input[], int input_len_bytes, const uint8_t inputpub[], int inputpub_len_bytes, T32 output[], int output_words)){
	//assert(input_len_bytes2 == 20);
	assert((input_len_bytes2 & 1) == 0);
	T32 output1[output_words];	
	func32(input, input_len_bytes2>>1, NULL, 0, output1, output_words);	
	func32(input + (input_len_bytes2>>1), input_len_bytes2>>1, NULL, 0, output, output_words);
	for(unsigned int i=0; i<output_words; i++){
		output[i] ^= output1[i];
	}
}

//  f(x ^ w) = y 
//  	where x, y are public,
//		w is private
template <typename T8, typename T32>
void f32_input_xor_pub(const T8 input[],
		int input_len_bytes, /*must be 10*/
		const uint8_t inputpub[], int inputpub_len_bytes,		
		T32 output[],
		int output_words,
		void (*func32)(const T8 input[], int input_len_bytes, const uint8_t inputpub[], int inputpub_len_bytes, T32 output[], int output_words)){
	assert(input_len_bytes == inputpub_len_bytes);
	T8 input_prepared[input_len_bytes];
	for(unsigned int i=0; i<input_len_bytes; i++){
		input_prepared[i] = input[i] ^ inputpub[i];
	}
	func32(input_prepared, input_len_bytes, NULL, 0, output, output_words);	
}

//---------------------------------------------------------------------
//                      some utilities
//---------------------------------------------------------------------
template <class T>
py::list to_pylist(std::vector<T>& v){
	py::list pylist;
	typedef typename std::vector<T>::iterator  itype;
	for (itype it = v.begin(); it!=v.end(); it++){
		pylist.append(*it);
	}
	return pylist;
}


template <class T>
std::vector<T> to_std_vector(const py::object& iterable){
    return std::vector<T>(py::stl_input_iterator<T>(iterable), py::stl_input_iterator<T>());
}

std::string zkboofunc_plain(const std::string & input, const std::string & inputpub, int output_bytes, 
		void (*func)  (const uint8_t* input, int input_len_bytes, 
			const uint8_t* inputpub, int inputpub_len_bytes,
			uint32_t* z, int output_in_words) );

py::tuple pyzkboo_prove_commit(const char* fname, const std::string &input, const std::string &inputpub, const std::string &output, 
		void (*func)(const MpcVariable<uint8_t>* input, int input_len_bytes, const uint8_t inputpub[], int inputpub_len_bytes, MpcVariable<uint32_t>* z, int output_in_words),		
		int (*func_randbytes_for_outputbytes)(int inputlen_bytes, int outputlen_bytes) );

py::tuple pyzkboo_fake_proof(const char* fname, int input_bytes_len, const std::string &inputpub, const std::string &output, const std::string &hash,
		void (*func)(const MpcVariableVerify<uint8_t>* input, int input_len_bytes, const uint8_t inputpub[], int inputpub_len_bytes, MpcVariableVerify<uint32_t>* z, int output_in_words),
		int (*func_randbytes_for_outputbytes)(int inputlen_bytes, int outputlen_bytes));

py::list pyzkboo_prove_response(const py::list &z_all, const std::string &hash32);

py::list pyzkboo_extract_es_from_Challenge(const std::string &hash32);

bool pyzkboo_verify(
		const char* fname, 
		int input_len_bytes, 
		const std::string &inputpub, 
		const std::string &output_plain, 
		const std::string &hash_v, 
		const std::string &proof_commit, 
		const py::list &z,
		void (*func)(
			const MpcVariableVerify<uint8_t>* input, 
			int input_len_bytes, 
			const uint8_t inputpub[], 
			int inputpub_len_bytes, 
			MpcVariableVerify<uint32_t>* z, 
			int output_in_words),
		int (*func_randbytes_for_outputbytes)(
			int inputlen_bytes, 
			int outputlen_bytes));

py::list pyzkboo_data_to_listbits(const std::string &data);

std::string pyzkboo_listbits_to_data(const py::list &bits);

std::string pyzkboo_xor_data(const std::string &a, const std::string &b);


//----------------------- python bindings for ZKBoo functions ------------------------------
int pyzkboo_rounds();


#endif /* ZKBOO_HELPER_H_ */