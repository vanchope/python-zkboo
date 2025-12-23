#include "zkboo_helper.h"

#include <stdio.h>
#include "assert.h"

namespace py = boost::python;


//------------------------------------------------------------------

std::string zkboofunc_plain(const std::string & input, const std::string & inputpub, int output_bytes, 
		void (*func)  (const uint8_t* input, int input_len_bytes, 
			const uint8_t* inputpub, int inputpub_len_bytes,
			uint32_t* z, int output_in_words) ){
	assert((output_bytes & (sizeof(uint32_t)-1)) == 0);
	int output_word32 = output_bytes / sizeof(uint32_t);
	uint32_t * output = new uint32_t[output_word32];
	(*func) ((uint8_t*)input.data(), input.size(), (uint8_t*)inputpub.data(), inputpub.size(), output, output_word32);
	std::string res((char*) output, (size_t) output_bytes);
	delete[] output;
	return res;
}
py::tuple pyzkboo_prove_commit(const char* fname, const std::string &input, const std::string &inputpub, const std::string &output, 
		void (*func)(const MpcVariable<uint8_t>* input, int input_len_bytes, const uint8_t inputpub[], int inputpub_len_bytes, MpcVariable<uint32_t>* z, int output_in_words),		
		int (*func_randbytes_for_outputbytes)(int inputlen_bytes, int outputlen_bytes) ){
	VecStr proof_committed_all_parts;
	std::string proof_commit = zkboo_prove_commit<uint32_t>(proof_committed_all_parts, 
		fname, input.data(), input.size(), inputpub.data(), inputpub.size(),
		output.data(), output.size(),
		func_randbytes_for_outputbytes(input.size(), output.size()),
		*func);	
	return py::make_tuple(proof_commit, to_pylist(proof_committed_all_parts));
}
py::tuple pyzkboo_fake_proof(const char* fname, int input_bytes_len, const std::string &inputpub, const std::string &output, const std::string &hash,
		void (*func)(const MpcVariableVerify<uint8_t>* input, int input_len_bytes, const uint8_t inputpub[], int inputpub_len_bytes, MpcVariableVerify<uint32_t>* z, int output_in_words),
		int (*func_randbytes_for_outputbytes)(int inputlen_bytes, int outputlen_bytes)){
	VecStr proof_committed_2parts;
	std::string proof_commit = zkboo_fake_prove<uint32_t>(proof_committed_2parts, 
		fname, (const unsigned char *) hash.data(), input_bytes_len, inputpub.data(), inputpub.size(), output.data(), output.size(),
		func_randbytes_for_outputbytes(input_bytes_len, output.size()),
		*func);
	return py::make_tuple(proof_commit, to_pylist(proof_committed_2parts));
}

//FIXME refactoring, it is just copied from mpc_core.h
//VecStr pyzkboo_prove_response(const VecStr &z_all, const std::string &hash32){
py::list pyzkboo_prove_response(const py::list &z_all, const std::string &hash32){
	//py::stl_input_iterator<std::string> begin(z_all), end;
	py::list res;
	int es[ZKBOO_NUMBER_OF_ROUNDS];
	extract_es_from_Challenge(es, (const unsigned char*) hash32.data());
	for(unsigned int i=0, j=0; i<py::len(z_all); i+=3, j++){
		if (es[j]==0){
			//res.push_back(z_all[i]);			
			//res.push_back(z_all[i+1]);
			res.append(z_all[i]);
			res.append(z_all[i+1]);
		}
		if (es[j]==1){
			res.append(z_all[i+1]);
			res.append(z_all[i+2]);
		}
		if (es[j]==2){
			res.append(z_all[i+2]);
			res.append(z_all[i]);
		}
	}
	return res;
}

py::list pyzkboo_extract_es_from_Challenge(const std::string &hash32){
	int es[ZKBOO_NUMBER_OF_ROUNDS];
	extract_es_from_Challenge(es, (const unsigned char*) hash32.data());
	py::list res;
	for(unsigned int i=0; i<ZKBOO_NUMBER_OF_ROUNDS; i++){
		res.append(es[i]);
	}
	return res;
}

bool pyzkboo_verify(const char* fname, int input_len_bytes, const std::string &inputpub, const std::string &output_plain, const std::string &hash_v, const std::string &proof_commit, const py::list &z,
		void (*func)(const MpcVariableVerify<uint8_t>* input, int input_len_bytes, const uint8_t inputpub[], int inputpub_len_bytes, MpcVariableVerify<uint32_t>* z, int output_in_words),
		int (*func_randbytes_for_outputbytes)(int inputlen_bytes, int outputlen_bytes)){
	std::vector<std::string> z_str = to_std_vector<std::string>(z);

	bool res = zkboo_verify<uint32_t>(fname, (const unsigned char *) hash_v.data(), inputpub.data(), inputpub.size(), output_plain.data(), output_plain.size(), 
		func_randbytes_for_outputbytes(input_len_bytes, output_plain.size()),
		*func,
		proof_commit,  z_str);
	return res;
}


py::list pyzkboo_data_to_listbits(const std::string &data){
	py::list res;
	for(unsigned int i=0; i<data.size(); i++){
		for(unsigned int j=0; j<8; j++){
			int bit = (data.data()[i] >> (7-j)) & 1;
			res.append(bit);
		}
	}
	return res;
}

std::string pyzkboo_listbits_to_data(const py::list &bits){
	std::vector<int> vbits = to_std_vector<int>(bits);
	unsigned int n = py::len(bits);
	assert((n & 7) == 0);  // divides 8
	unsigned int bytes = n >> 3;
	char data[bytes]; // bits to bytes
	unsigned int bits_offset = 0;
	for(unsigned int i=0; i<bytes; i++){
		data[i] = 0;
		for(unsigned int j=0; j<8; j++){
			data[i] = (data[i] << 1) + vbits[bits_offset++];
		}
	}
	return std::string(data, bytes);
}


std::string pyzkboo_xor_data(const std::string &a, const std::string &b){
	assert(a.size() == b.size());
	int N = a.size();
	const char *as = a.data();
	const char *bs = b.data();
	char c[N];
	for(int i=0; i<N; i++){
		c[i] = as[i] ^ bs[i];
	}
	return std::string(c, N);
}

int pyzkboo_rounds(){
	return ZKBOO_NUMBER_OF_ROUNDS;
}
