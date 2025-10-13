#!/bin/sh

echo "Starting compilation"

CC=gcc
CFLAG="" #-Wall -Werror -Wpedantic"
INCLUDES="-lbcm2835"

echo "Finished declarations"

#$CC screentest.c $CFLAGS $INCLUDES -o screentest.out
$CC screentest.c $CFLAGS $INCLUDES

echo "Build successful"
