#include <stdio.h>
#include "assert.h"
#include <vector>

#include <boost/python.hpp>

using namespace boost::python;


/*
list aes_init_keys(const std::string& key_data, const std::string& salt, int nrounds){
	EVP_CIPHER_CTX * enc, *dec;	
	if(i != 16){		
		exit(1);
	}	
	EVP_EncryptInit_ex(enc,EVP_aes_128_cbc(), NULL, key, iv);	
	list res;
	res.append((long)enc);
	res.append((long)dec);
//	res.push_back((long)enc);
	return res;
}
*/

//void aes_dispose(long ptr){
//	EVP_CIPHER_CTX * ctx = (EVP_CIPHER_CTX *) ptr;
//}

/*
std::string aes_encrypt (long ptr, const std::string& data){
	int dataLength = data.size();
	EVP_CIPHER_CTX * enc = (EVP_CIPHER_CTX *) ptr;

	int c_len = dataLength + AES_BLOCK_SIZE;
	int f_len = 0;
	unsigned char *ciphertext = (unsigned char*) malloc(c_len);

	EVP_EncryptInit_ex(enc, NULL, NULL, NULL, NULL);
	EVP_EncryptUpdate(enc, ciphertext, &c_len, (unsigned char*) data.c_str(), dataLength);
	EVP_EncryptFinal_ex(enc, ciphertext+c_len, &f_len);

	int outLen = c_len + f_len;
	assert (outLen % AES_BLOCK_SIZE == 0);

	std::string res((char*) ciphertext, (size_t) outLen);	
	free(ciphertext);
	return res;
}
*/


BOOST_PYTHON_MODULE(pyzkboopp)
{
	//def("chacha_plain", chacha_plain);
	//def("trivium_plain", trivium_plain);
}