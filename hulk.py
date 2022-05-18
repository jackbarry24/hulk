#!/usr/bin/env python3

import concurrent.futures
import hashlib
import os
import string
import sys

# Constants

ALPHABET = string.ascii_lowercase + string.digits

# Functions

def usage(exit_code=0):
    progname = os.path.basename(sys.argv[0])
    print(f'''Usage: {progname} [-a ALPHABET -c CORES -l LENGTH -p PATH -s HASHES]
    -a ALPHABET Alphabet to use in permutations
    -c CORES    CPU Cores to use
    -l LENGTH   Length of permutations
    -p PREFIX   Prefix for all permutations
    -s HASHES   Path of hashes file''')
    sys.exit(exit_code)

def md5sum(s):
    return hashlib.md5(str.encode(s)).hexdigest()

def permutations(length, alphabet=ALPHABET):
    ''' Recursively yield all permutations of alphabet up to given length. '''
    
    if length <= 0:
        yield ''

    elif length == 1:
        for letter in alphabet:
            yield letter

    else:
        for letter in alphabet:
            for perm in permutations(length -1, alphabet):
                yield letter + perm

def flatten(sequence):
    ''' Flatten sequence of iterators. '''
    
    for sub_sequence in sequence:
        yield from sub_sequence

def crack(hashes, length, alphabet=ALPHABET, prefix=''):
    ''' Return all password permutations of specified length that are in hashes
    by sequentially trying all permutations. '''
  
    return [prefix + passw for passw in permutations(length, alphabet) if md5sum(prefix + passw) in hashes ]

def whack(arguments):
    ''' Call the crack function with the specified list of arguments '''
    
    return crack(*arguments)

def smash(hashes, length, alphabet=ALPHABET, prefix='', cores=1):
    ''' Return all password permutations of specified length that are in hashes
    by concurrently subsets of permutations concurrently.
    '''

    arguments = ((hashes, length - len(letter), alphabet, prefix + letter) for letter in alphabet)
    with concurrent.futures.ProcessPoolExecutor(cores) as executor:
        solution = flatten(executor.map(whack, arguments))
    return solution

# Main Execution

def main():
    arguments   = sys.argv[1:]
    alphabet    = ALPHABET
    cores       = 1
    hashes_path = 'hashes.txt'
    length      = 1
    prefix      = ''

    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-h':
            usage()
        elif argument == '-a':
            alphabet = arguments.pop(0)
        elif argument == '-c':
            cores = int(arguments.pop(0))
        elif argument == '-l':
           length = int(arguments.pop(0))
        elif argument == '-p':
            prefix += arguments.pop(0)
        elif argument == '-s':
            hashes_path = arguments.pop(0)
        else:
            usage(1)
 

    hashes_set = set()
    hashes = open(hashes_path, 'r')
    for line in hashes:
        hashes_set.add(line.rstrip())
    hashes.close()
        

    for password in smash(hashes_set, length, alphabet, prefix, cores):
        print(password)
       
if __name__ == '__main__':
    main()

# vim: set sts=4 sw=4 ts=8 expandtab ft=python:
