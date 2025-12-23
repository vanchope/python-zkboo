#include <boost/python.hpp>
#include "zkboo_helper.h"

namespace py = boost::python;

BOOST_PYTHON_MODULE(pyzkboo_helper)
{
	py::class_<VecStr>("VecStr")
        .def(py::vector_indexing_suite<VecStr>() );
	
	py::def("get_MpcPartyView_input_offset", get_MpcPartyView_input_offset);
	py::def("pyzkboo_rounds", pyzkboo_rounds);	
	py::def("pyzkboo_extract_es_from_Challenge", pyzkboo_extract_es_from_Challenge);
	py::def("pyzkboo_data_to_listbits", pyzkboo_data_to_listbits);
	py::def("pyzkboo_listbits_to_data", pyzkboo_listbits_to_data);
	py::def("pyzkboo_xor_data", pyzkboo_xor_data);
	
	py::def("pyzkboo_prove_response", pyzkboo_prove_response);		
}