
# TODO: replace this Makefile craziness by a good setup.py or a scons file

# I use this on my machine to compile for the OpenMoko :
# I need to use the ToolChain header files

PYTHON_CFLAGS = -I/usr/local/openmoko/arm/arm-angstrom-linux-gnueabi/usr/include/python2.5

# On my machine I uncomment this to compile using my local python headers
# PYTHON_CFLAGS = -I/usr/include/python2.5/

# For some reason I need to not assume strict aliasing (only for the arm version) !
CFLAGS = $(PYTHON_CFLAGS) -L/usr/local/openmoko/arm/usr/lib/ -O3 -fno-strict-aliasing

all: geo.so cobject.so widget.so frame.so painter.so sdl_painter.so window.so surf_widget.so image.so version.so

all_c: geo.c cobject.c widget.c frame.c painter.c sdl_painter.c window.c surf_widget.c image.c version.c


CYTHON = cython


%.so: %.o
	$(CC) -shared $< -I. $(CFLAGS) -o $@
%.o : %.c
	$(CC) -c -fPIC -I. $(CFLAGS) $< -o $@
%.c : %.pyx
	$(CYTHON) -I. $<

sdl_painter.so: sdl_painter.o
	$(CC) -shared sdl_painter.o `sdl-config --libs` -I. $(CFLAGS) -o sdl_painter.so
sdl_painter.o : sdl_painter.c
	$(CC) -c -fPIC -I.  `sdl-config --cflags` $(CFLAGS) sdl_painter.c -o sdl_painter.o
sdl_painter.c : sdl_painter.pyx
	$(CYTHON) -I. sdl_painter.pyx


clean:
	rm -f *.o *.c *.so
