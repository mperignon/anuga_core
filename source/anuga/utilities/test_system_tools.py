#!/usr/bin/env python


import unittest
import tempfile
import random
import Numeric as num
import zlib
from os.path import join, split, sep
from anuga.config import netcdf_mode_r, netcdf_mode_w, netcdf_mode_a


# Please, don't add anuga.utilities to these imports.
# I'm trying to keep this file general, so it works for EQRM and ANUGA
# EQRM also uses this file, but has a different directory structure
from system_tools import *

class Test_system_tools(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_user_name(self):
        user = get_user_name()

        # print user
        assert isinstance(user, basestring), 'User name should be a string'

    def test_host_name(self):
        host = get_host_name()

        # print host
        assert isinstance(host, basestring), 'User name should be a string'        

    def test_compute_checksum(self):
        """test_compute_checksum(self):

        Check that checksums on files are OK
        """

        from tempfile import mkstemp, mktemp

        # Generate a text file
        tmp_fd , tmp_name = mkstemp(suffix='.tmp', dir='.')
        fid = os.fdopen(tmp_fd, 'w+b')
        string = 'My temp file with textual content. AAAABBBBCCCC1234'
        fid.write(string)
        fid.close()

        # Have to apply the 64 bit fix here since we aren't comparing two
        # files, but rather a string and a file.
        ref_crc = safe_crc(string)

        checksum = compute_checksum(tmp_name)
        assert checksum == ref_crc

        os.remove(tmp_name)
        


        # Binary file
        tmp_fd , tmp_name = mkstemp(suffix='.tmp', dir='.')
        fid = os.fdopen(tmp_fd, 'w+b')

        string = 'My temp file with binary content. AAAABBBBCCCC1234'
        fid.write(string)
        fid.close()

        ref_crc = safe_crc(string)
        checksum = compute_checksum(tmp_name)

        assert checksum == ref_crc

        os.remove(tmp_name)        
        
        # Binary NetCDF File X 2 (use mktemp's name)

        try:
            from Scientific.IO.NetCDF import NetCDFFile
        except ImportError:
            # This code is also used by EQRM which does not require NetCDF
            pass
        else:
            test_array = num.array([[7.0, 3.14], [-31.333, 0.0]])

            # First file
            filename1 = mktemp(suffix='.nc', dir='.')
            fid = NetCDFFile(filename1, netcdf_mode_w)
            fid.createDimension('two', 2)
            fid.createVariable('test_array', num.Float,
                               ('two', 'two'))
            fid.variables['test_array'][:] = test_array
            fid.close()
            
            # Second file
            filename2 = mktemp(suffix='.nc', dir='.')
            fid = NetCDFFile(filename2, netcdf_mode_w)
            fid.createDimension('two', 2)
            fid.createVariable('test_array', num.Float,
                               ('two', 'two'))
            fid.variables['test_array'][:] = test_array
            fid.close()
            
            
            checksum1 = compute_checksum(filename1)
            checksum2 = compute_checksum(filename2)        
            assert checksum1 == checksum2


            os.remove(filename1)
            os.remove(filename2)


    def test_compute_checksum_real(self):
        """test_compute_checksum(self):

        Check that checksums on a png file is OK
        """

        # Get path where this test is run
        # I'm trying to keep this file general, so it works for EQRM and ANUGA
        path, tail = split(__file__)
        if path == '':
            path = '.' + sep
        
        filename = path + sep +  'crc_test_file.png'

        ref_crc = 1203293305 # Computed on Windows box
        checksum = compute_checksum(filename)

        msg = 'Computed checksum = %s, should have been %s'\
              %(checksum, ref_crc)
        assert checksum == ref_crc, msg
        #print checksum
        

    def test_get_vars_in_expression(self):
        '''Test the 'get vars from expression' code.'''

        def test_it(source, expected):
            result = get_vars_in_expression(source)
            result.sort()
            expected.sort()
            msg = ("Source: '%s'\nResult: %s\nExpected: %s"
                   % (source, str(result), str(expected)))
            self.failUnlessEqual(result, expected, msg)
                
        source = 'fred'
        expected = ['fred']
        test_it(source, expected)

        source = 'tom + dick'
        expected = ['tom', 'dick']
        test_it(source, expected)

        source = 'tom * (dick + harry)'
        expected = ['tom', 'dick', 'harry']
        test_it(source, expected)

        source = 'tom + dick**0.5 / (harry - tom)'
        expected = ['tom', 'dick', 'harry']
        test_it(source, expected)


    def test_tar_untar_files(self):
        '''Test that tarring & untarring files is OK.'''

        num_lines = 100
        line_size = 100

        # these test files must exist in the current directory
        # create them with random data
        files = ('alpha', 'beta', 'gamma')
        for file in files:
            fd = open(file, 'w')
            line = ''
            for i in range(num_lines):
                for j in range(line_size):
                    line += chr(random.randint(ord('A'), ord('Z')))
                line += '\n'
                fd.write(line)
            fd.close()

        # name of tar file and test (temp) directory
        tar_filename = 'test.tgz'
        tmp_dir = tempfile.mkdtemp()

        # tar and untar the test files into a temporary directory
        tar_file(files, tar_filename)
        untar_file(tar_filename, tmp_dir)

        # see if original files and untarred ones are the same
        for file in files:
            fd = open(file, 'r')
            orig = fd.readlines()
            fd.close()

            fd = open(os.path.join(tmp_dir, file), 'r')
            copy = fd.readlines()
            fd.close()

            msg = "Original file %s isn't the same as untarred copy?" % file
            self.failUnless(orig == copy, msg)

        # clean up
        for file in files:
            os.remove(file)
        os.remove(tar_filename)


    def test_file_digest(self):
        '''Test that file digest functions give 'correct' answer.
        
        Not a good test as we get 'expected_digest' from a digest file,
        but *does* alert us if the digest algorithm gives us a different string.
        '''

        # we expect this digest string from the data file
        expected_digest = '831a1dde6edd365ec4163a47871fa21b'

        # prepare test directory and filenames
        tmp_dir = tempfile.mkdtemp()
        data_file = os.path.join(tmp_dir, 'test.data')
        digest_file = os.path.join(tmp_dir, 'test.digest')

        # create the data file
        data_line = 'The quick brown fox jumps over the lazy dog. 0123456789\n'
        fd = open(data_file, 'w')
        for line in range(100):
            fd.write(data_line)
        fd.close()

        # create the digest file
        make_digest_file(data_file, digest_file)

        # get digest string for the data file
        digest = get_file_hexdigest(data_file)

        # check that digest is as expected, string
        msg = ("Digest string wrong, got '%s', expected '%s'"
               % (digest, expected_digest))
        self.failUnless(expected_digest == digest, msg)

        # check that digest is as expected, file
        msg = ("Digest file wrong, got '%s', expected '%s'"
               % (digest, expected_digest))
        fd = open(digest_file, 'r')
        digest = fd.readline()
        fd.close()
        self.failUnless(expected_digest == digest, msg)

    def test_file_length_function(self):
        '''Test that file_length() give 'correct' answer.'''

        # prepare test directory and filenames
        tmp_dir = tempfile.mkdtemp()
        test_file1 = os.path.join(tmp_dir, 'test.file1')
        test_file2 = os.path.join(tmp_dir, 'test.file2')
        test_file3 = os.path.join(tmp_dir, 'test.file3')
        test_file4 = os.path.join(tmp_dir, 'test.file4')

        # create files of known length
        fd = open(test_file1, 'w')      # 0 lines
        fd.close
        fd = open(test_file2, 'w')      # 5 lines, all '\n'
        for i in range(5):
            fd.write('\n')
        fd.close()
        fd = open(test_file3, 'w')      # 25 chars, no \n, 1 lines
        fd.write('no newline at end of line')
        fd.close()
        fd = open(test_file4, 'w')      # 1000 lines
        for i in range(1000):
            fd.write('The quick brown fox jumps over the lazy dog.\n')
        fd.close()

        # use file_length() to get and check lengths
        size1 = file_length(test_file1)
        msg = 'Expected file_length() to return 0, but got %d' % size1
        self.failUnless(size1 == 0, msg)
        size2 = file_length(test_file2)
        msg = 'Expected file_length() to return 5, but got %d' % size2
        self.failUnless(size2 == 5, msg)
        size3 = file_length(test_file3)
        msg = 'Expected file_length() to return 1, but got %d' % size3
        self.failUnless(size3 == 1, msg)
        size4 = file_length(test_file4)
        msg = 'Expected file_length() to return 1000, but got %d' % size4
        self.failUnless(size4 == 1000, msg)

        
#-------------------------------------------------------------
if __name__ == "__main__":
    suite = unittest.makeSuite(Test_system_tools, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

