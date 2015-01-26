from anuga.utilities.data_audit_wrapper import IP_verified
from tempfile import mktemp

import os

buildroot = os.getcwd()



os.chdir('source')
os.chdir('anuga')
print
print '======================= anuga tests ================================='    
print 'Changing to', os.getcwd() # This is now different from buildroot   
execfile('test_all.py')




# Try to run parallel tests if pypar is installed
from anuga import pypar_available
   
if pypar_available:
    os.chdir(buildroot)
    os.chdir('source')
    os.chdir('anuga')
    os.chdir('parallel')
    os.chdir('test')
    print
    print '===================== anuga parallel tests =========================='
    print 'Changing to', os.getcwd()
    execfile('test_all.py')
else:
    print 'anuga.parallel tests not run as pypar not installed'





# FIXME SR 20130327: Just commenting out this comment to run the validation tests.
# We are currently undating the automated validation tests, so at present this point to
# something which most people do not get as part of the download. We will update and
# point them to the new validation_tests in future.
"""
print
print '************************** NOTE *************************************'
print 'If all unit tests passed you should run the suite of validation tests'
print 'Go to the directory anuga_validation/automated_validation_tests'
print 'and run'
print '    python validate_all.py'
print
print 'These tests will take a few hours and will verify that ANUGA'
print 'produces the physical results expected.'
print '*********************************************************************'
"""


# Temporary bail out
import sys; sys.exit() 


#---------------------------
# IP Data Audit (in source/anuga directory as well)
#---------------------------

# Create temporary area for svn to export source files
# FIXME (Ole): It would be good to make sure these files
# are exactly the same as those walked over by the
# release script: create_distribution.
#
# Come to think of it - this is probably not the best
# place for this check. It may have to move up one level.
# What do you all think?



temp_dir = mktemp()

print 'Temp dir', temp_dir
os.mkdir(temp_dir)

# Get the ANUGA core source files
s = 'svn export . %s%sanuga' %(temp_dir, os.sep) 
print s
os.system(s)

print 'Verifying data IP'
if not IP_verified(temp_dir):
    msg = 'Files have not been verified for IP.\n'
    msg += 'Each data file must have a license file with it.'
    raise Exception, msg





    
