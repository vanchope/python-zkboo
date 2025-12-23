SRCS=$(wildcard *.cpp)
#LOCAL_HOME = ../venv_cpp/
INCLUDE = -I/usr/include -I../ZKBOOpp/inc
LIBPATH = -L. -L/usr/lib -L../ZKBOOpp/target

#CXXFLAGS= ${INCLUDE} -g -O0 -Wall -fPIC -std=c++11
# $(ARCH)
PYTHONINC = `python-config --includes`
PYTHONLDFLAGS = `python-config --ldflags`
BOOST_INC = /usr/include
BOOST_LIB = /usr/lib

#PY_TARGET = pytrivium pychacha #pyzkboopp
#python: $(PY_TARGET).so

python: pyzkboo_helper.so pytrivium.so pysha256.so 
#pychacha.so 


COMMON_OBJS = zkboo_helper.o

libzkboohelper.a:  $(COMMON_OBJS)
	ar rcs $@ $^


%.so: %.o 
	g++ -shared -Wl,-soname,$(PY_TARGET).so \
	$< -L$(BOOST_LIB) -lboost_python -fPIC \
	$(PYTHONLDFLAGS) \
	-o $@ -I. $(LIBPATH) -lzkboohelper -lzkboopp
#$(ARCH)

# -std=c++11 brings problems with compilation?
%.o: %.cpp libzkboohelper.a 
	g++  $(PYTHONINC) -I$(BOOST_INC) -c $< -fPIC $(INCLUDE) -L. -lzkboohelper -lzkboopp

# $(PY_TARGET).so: $(PY_TARGET).o
# 	g++ -shared -Wl,-soname,$(PY_TARGET).so \
# 	$(PY_TARGET).o -L$(BOOST_LIB) -lboost_python -fPIC \
# 	$(PYTHONLDFLAGS) \
# 	-o $(PY_TARGET).so -I. $(LIBPATH) $(ARCH)

# $(PY_TARGET).o: $(PY_TARGET).cpp 
# 	g++ $(PYTHONINC) -I$(BOOST_INC) -c $(PY_TARGET).cpp -fPIC $(INCLUDE) -L. $(ARCH)

zkboo_helper.o: zkboo_helper.h

clean:
	rm *o *.a




# Help:
# all: library.cpp main.cpp
#
#    $@ evaluates to all
#    $< evaluates to library.cpp
#    $^ evaluates to library.cpp main.cpp
