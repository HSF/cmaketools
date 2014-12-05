"""
Wrapper to run the tests.
"""
import os
from nose import main

main(defaultTest=os.path.normpath(__file__+"/../.."))
