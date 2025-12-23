#include <stdio.h>
#include "assert.h"

#include <boost/python.hpp>

#include "chacha/chacha.h"

using namespace boost::python;

std::string chacha_plain(const std::string & input, int output_word32){
	uint32_t * output = new uint32_t[output_word32];
	int length = input.size();	
	chacha<uint8_t, uint32_t, uint64_t>((uint8_t*)input.c_str(), length, output, output_word32);
	std::string res((char*) output, (size_t) output_word32 * sizeof(uint32_t));
	delete[] output;
	return res;
}

BOOST_PYTHON_MODULE(pychacha)
{
	def("chacha_plain", chacha_plain);	
}