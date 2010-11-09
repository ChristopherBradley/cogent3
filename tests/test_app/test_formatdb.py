#!/usr/bin/env python
# Author: Greg Caporaso (gregcaporaso@gmail.com)
# test_formatdb.py

""" Description
File created on 16 Sep 2009.

"""
from __future__ import division
from os.path import split, exists
from cogent import LoadSeqs
from cogent.util.unit_test import TestCase, main
from cogent.app.util import get_tmp_filename
from cogent.util.misc import remove_files
from cogent.app.blast import blastn
from cogent.app.formatdb import FormatDb, build_blast_db_from_seqs,\
    build_blast_db_from_fasta_path, build_blast_db_from_fasta_file

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2007-2009, The Cogent Project"
__credits__ = ["Greg Caporaso"]
__license__ = "GPL"
__version__ = "1.6.0.dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"
__status__ = "Production"

class FormatDbTests(TestCase):
    
    def setUp(self):
        self.in_seqs1_fp =\
         get_tmp_filename(prefix='FormatDbTests',suffix='.fasta')
        self.in_seqs1_file = open(self.in_seqs1_fp,'w')
        self.in_seqs1_file.write(in_seqs1)
        self.in_seqs1_file.close()
        self.in_seqs1 = LoadSeqs(self.in_seqs1_fp,aligned=False)
        self.test_seq = test_seq
        
        self.in_aln1_fp =\
         get_tmp_filename(prefix='FormatDbTests',suffix='.fasta')
        self.in_aln1_file = open(self.in_aln1_fp,'w')
        self.in_aln1_file.write(in_aln1)
        self.in_aln1_file.close()
        self.in_aln1 = LoadSeqs(self.in_aln1_fp)
        
        
        self.files_to_remove = [self.in_seqs1_fp,self.in_aln1_fp]
    
    def tearDown(self):
        remove_files(self.files_to_remove)
        
    def test_call(self):
        """FormatDb: Calling on a nucleotide data functions as expected
        """
        fdb = FormatDb(WorkingDir='/tmp')
        result = fdb(self.in_seqs1_fp)
        
        # test sucessful run
        self.assertEqual(result['ExitStatus'],0)
        
        expected_result_keys = set(\
         ['log','nhr','nin','nsd','nsi','nsq','ExitStatus','StdOut','StdErr'])
        self.assertEqual(set(result.keys()),expected_result_keys)
        
        inputfile_basename = split(self.in_seqs1_fp)[1]
        # got all the expected out files, and filepaths are as expected
        outpaths = []
        for ext in ['log','nhr','nin','nsd','nsi','nsq']:
            outpath = '/tmp/%s.%s' % (inputfile_basename,ext)
            outpaths.append(outpath)
            self.assertEqual(result[ext].name,outpath)
        result.cleanUp()
        
        # all created files are cleaned up
        for outpath in outpaths:
            self.assertFalse(exists(outpath),\
             "%s was not cleaned up." % outpath)
    
    def test_blast_against_new_db(self):
        """Formatdb: blastall against a newly created DB functions as expected
        """
        fdb = FormatDb(WorkingDir='/tmp')
        result = fdb(self.in_seqs1_fp)
        blast_res = blastn(self.test_seq,blast_db=self.in_seqs1_fp)
        result.cleanUp()
        
        # Test that a blast result was returned
        self.assertTrue('s1' in blast_res,\
         "Not getting any blast results.")
        # Test that the sequence we expect was a good blast hit
        subject_ids = [r['SUBJECT ID'] for r in blast_res['s1'][0]]
        self.assertTrue('11472384' in subject_ids,\
         "Not getting expected blast results.")
         
    def test_build_blast_db_from_seqs(self):
        """build_blast_db_from_seqs convenience function works as expected
        """
        blast_db, db_files = build_blast_db_from_seqs(self.in_seqs1,output_dir='/tmp')
        self.assertTrue(blast_db.startswith('/tmp/Blast_tmp_db'))
        self.assertTrue(blast_db.endswith('.fasta'))
        expected_db_files = set([blast_db + ext\
         for ext in ['.nhr','.nin','.nsq','.nsd','.nsi','.log']])
        self.assertEqual(set(db_files),expected_db_files)
        
        # result returned when blasting against new db
        self.assertEqual(\
            len(blastn(self.test_seq,blast_db=blast_db)),1)
            
        # Make sure all db_files exist
        for fp in db_files:
            self.assertTrue(exists(fp))
        
        # Remove all db_files exist   
        remove_files(db_files)
        
        # Make sure nothing weird happened in the remove
        for fp in db_files:
            self.assertFalse(exists(fp))
        
    def test_build_blast_db_from_fasta_path(self):
        """build_blast_db_from_fasta_path convenience function works as expected
        """
        blast_db, db_files = \
         build_blast_db_from_fasta_path(self.in_seqs1_fp)
        self.assertEqual(blast_db,self.in_seqs1_fp)
        expected_db_files = set([self.in_seqs1_fp + ext\
         for ext in ['.nhr','.nin','.nsq','.nsd','.nsi','.log']])
        self.assertEqual(set(db_files),expected_db_files)

        # result returned when blasting against new db
        self.assertEqual(\
            len(blastn(self.test_seq,blast_db=blast_db)),1)

        # Make sure all db_files exist
        for fp in db_files:
            self.assertTrue(exists(fp))
        
        # Remove all db_files exist   
        remove_files(db_files)
        
        # Make sure nothing weird happened in the remove
        for fp in db_files:
            self.assertFalse(exists(fp))
            
    def test_build_blast_db_from_fasta_path_aln(self):
        """build_blast_db_from_fasta_path works with alignment as input
        """
        blast_db, db_files = build_blast_db_from_fasta_path(self.in_aln1_fp)
        self.assertEqual(blast_db,self.in_aln1_fp)
        expected_db_files = set([blast_db + ext\
         for ext in ['.nhr','.nin','.nsq','.nsd','.nsi','.log']])
        self.assertEqual(set(db_files),expected_db_files)
        # result returned when blasting against new db
        self.assertEqual(\
            len(blastn(self.test_seq,blast_db=blast_db,e_value=0.0)),1)
        
        # Make sure all db_files exist
        for fp in db_files:
            self.assertTrue(exists(fp))
        
        # Remove all db_files exist   
        remove_files(db_files)
        
        # Make sure nothing weird happened in the remove
        for fp in db_files:
            self.assertFalse(exists(fp))
            
    def test_build_blast_db_from_fasta_file(self):
        """build_blast_db_from_fasta_file works with open files as input
        """
        blast_db, db_files = \
         build_blast_db_from_fasta_file(open(self.in_aln1_fp),output_dir='/tmp/')
        self.assertTrue(blast_db.startswith('/tmp/BLAST_temp_db'))
        self.assertTrue(blast_db.endswith('.fasta'))
        expected_db_files = set([blast_db] + [blast_db + ext\
         for ext in ['.nhr','.nin','.nsq','.nsd','.nsi','.log']])
        self.assertEqual(set(db_files),expected_db_files)
        # result returned when blasting against new db
        self.assertEqual(\
            len(blastn(self.test_seq,blast_db=blast_db,e_value=0.0)),1)
        
        # Make sure all db_files exist
        for fp in db_files:
            self.assertTrue(exists(fp))
        
        # Remove all db_files exist   
        remove_files(db_files)
        
        # Make sure nothing weird happened in the remove
        for fp in db_files:
            self.assertFalse(exists(fp))
        

in_seqs1 = """>11472286
GATGAACGCTGGCGGCATGCTTAACACATGCAAGTCGAACGGAACACTTTGTGTTTTGAGTTAATAGTTCGATAGTAGATAGTAAATAGTGAACACTATGAACTAGTAAACTATTTAACTAGAAACTCTTAAACGCAGAGCGTTTAGTGGCGAACGGGTGAGTAATACATTGGTATCTACCTCGGAGAAGGACATAGCCTGCCGAAAGGTGGGGTAATTTCCTATAGTCCCCGCACATATTTGTTCTTAAATCTGTTAAAATGATTATATGTTTTATGTTTATTTGATAAAAAGCAGCAAGACAAATGAGTTTTATATTGGTTATACAGCAGATTTAAAAAATAGAATTAGGTCTCATAATCAGGGAGAAAACAAATCAACTAAATCTAAAATACCTTGGGAATTGGTTTACTATGAAGCCTACAAAAACCAAACATCAGCAAGGGTTAGAGAATCAAAGTTGAAACATTATGGGCAATCATTAACTAGACTTAAGAGAAGAATTGGTTTTTGAGAACAAATATGTGCGGGGTAAAGCAGCAATGCGCTCCGAGAGGAACCTCTGTCCTATCAGCTTGTTGGTAAGGTAATGGCTTACCAAGGCGACGACGGGTAGCTGGTGTGAGAGCACGACCAGCCACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGAGGAATTTTCCACAATGGGCGCAAGCCTGATGGAGCAATGCCGCGTGAAGGATGAAGATTTTCGGATTGTAAACTTCTTTTAAGTAGGAAGATTATGACGGTACTACTTGAATAAGCATCGGCTAACTACGTGCCAGCAGCCGCGGTAATACGTAGGATGCAAGCGTTATCCGGAATTACTGGGCGTAAAGCGTGTGTAGGTGGTTTATTAAGTTAAATGTTAAATTTTCAGGCTTAACTTGGAAACCGCATTTAATACTGGTAGACTTTGAGGACAAGAGAGGCAGGCGGAATTAGCGGAGTAGCGGTGAAATGCGTAGATATCGCTAAGAACACCAATGGCGAAGGCAGCCTGCTGGTTTGCACCTGACACTGAGATACGAAAGCGTGGGGAGCGAACGGGATTAGATACCCCGGTAGTCCACGCCGTAAACGATGGTCACTAGCTGTTAGGGGCTCGACCCCTTTAGTAGCGAAGCTAACGCGTTAAGTGACCCGCCTGGGGAGTACGATCGCAAGATTAAAACTCAAAGGAATTGACGGGGACCCGCACAAGCGGTGGAACGTGAGGTTTAATTCGTCTCTAAGCGAAAAACCTTACCGAGGCTTGACATCTCCGGAAGACCTTAGAAATAAGGTTGTGCCCGAAAGGGAGCCGGATGACAGGTGCTGCATGGCTGTCGTCAGCTCGTGTTGTGAAATGTTCGGTTAAGTCCGTTAACGAGCGCAACCCTTGCTGTGTGTTGTATTTTTCACACAGGACTATCCTGGTCAACAGGGAGGAAGGTGGGGATGACGTCAAGTCAGCATGGCTCTTACGCCTCGGGCTACACTCGCGTTACAATGGCCGGTACAATGGGCTGCCAACTCGTAAGGGGGAGCTAATCCCATCAAAACCGGTCCCAGTTCGGATTGAGGGCTGCAATTCGCCCTCATGAAGTCGGAATCGCTAGTAACCGCGAATCAGCACGTCGCGGTGAATGCGTTCTCGGGTCTTGTACACACTGCCCGTCACACCACGAAAGTTAGTAACGCCCGAAGTGCCCTGTATGGGGTCCTAAGGTGGGGCTAGCGATTGGGGTG
>11472384
AGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCATGCCTTACACATGCAAGTCGAACGGCAGCACGGGGGCAACCCTGGTGGCGAGTGGCGAACGGGTGAGTAATACATCGGAACGTGTCCTGTAGTGGGGGATAGCCCGGCGAAAGCCGGATTAATACCGCATACGCTCTACGGAGGAAAGGGGGGGATCTTAGGACCTCCCGCTACAGGGGCGGCCGATGGCAGATTAGCTAGTTGGTGGGGTAAAGGCCTACCAAGGCGACGATCTGTAGCTGGTCTGAGAGGACGACCAGCCACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATTTTGGACAATGGGGGCAACCCTGATCCAGCAATGCCGCGTGTGTGAAGAAGGCCTTCGGGTTGTAAAGCACTTTTGTCCGGAAAGAAAACGCCGTGGTTAATACCCGTGGCGGATGACGGTACCGGAAGAATAAGCACCGGCTAACTACGTGCCAGCAGCCGCGGTAATACGTAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGTGCGCAGGCGGTCCGCTAAGACAGATGTGAAATCCCCGGGCTTAACCTGGGAACTGCATTTGTGACTGGCGGGCTAGAGTATGGCAGAGGGGGGTAGAATTCCACGTGTAGCAGTGAAATGCGTAGAGATGTGGAGGAATACCGATGGCGAAGGCAGCCCCCTGGGCCAATACTGACGCTCATGCACGAAAGCGTGGGGAGCAAACAGGATTAGATACCCTGGTAGTCCACGCCCTAAACGATGTCAACTAGTTGTCGGGTCTTCATTGACTTGGTAACGTAGCTAACGCGTGAAGTTGACCGCCTGGGGAGTACGGTCGCAAGATTAAAACTCAAAGGAATTGACGGGGACCCGCACAAGCGGTGGATGATGTGGATTAATTCGATGCAACGCGAAAAACCTTACCTACCCTTGACATGTATGGAATCCTGCTGAGAGGTGGGAGTGCCCGAAAGGGAGCCATAACACAGGTGCTGCATGGCTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTTGTCCCTAGTTGCTACGCAAGAGCACTCTAGGGAGACTGCCGGTGACAAACCGGAGGAAGGTGGGGATGACGTCAAGTCCTCATGGCCCTTATGGGTAGGGCTTCACACGTCATACAATGGTCGGAACAGAGGGTCGCCAACCCGCGAGGGGGAGCCAATCCCAGAAAACCGATCGTAGTCCGGATCGCACTCTGCAACTCGAGTGCGTGAAGCTGGAATCGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTCACACCATGGGAGTGGGTTTTACCAGAAGTGGCTAGTCTAACCGCAAGGAGGACGGTCACCACGGTAGGATTCATGACTGGGGTGAAGTCGTAACAAGGTAGCCGTATCGGAAGGTGCGGCTGGATCACCTCCTTTCTCGAGCGAACGTGTCGAACGTTGAGCGCTCACGCTTATCGGCTGTGAAATTAGGACAGTAAGTCAGACAGACTGAGGGGTCTGTAGCTCAGTCGGTTAGAGCACCGTCTTGATAAGGCGGGGGTCGATGGTTCGAATCCATCCAGACCCACCATTGTCT
>11468680
TAAACTGAAGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCATGCCTTACACATGCAAGTCGAACGGCAGCACGGGTGCTTGCACCTGGTGGCGAGTGGCGAACGGGTGAGTAATACATCGGAACATGTCCTGTAGTGGGGGATAGCCCGGCGAAAGCCGGATTAATACCGCATACGATCTACGGATGAAAGCGGGGGACCTTCGGGCCTCGCGCTATAGGGTTGGCCGATGGCTGATTAGCTAGTTGGTGGGGTAAAGGCCTACCAAGGCGACGATCAGTAGCTGGTCTGAGAGGACGACCAGCCACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATTTTGGACAATGGGCGAAAGCCTGATCCAGCAATGCCGCGTGTGTGAAGAAGGCCTTCGGGTTGTAAAGCACTTTTGTCCGGAAAGAAATCCTTGGCTCTAATACAGTCGGGGGATGACGGTACCGGAAGAATAAGCACCGGCTAACTACGTGCCAGCAGCCGCGGTAATACGTAGGGTGCGAGCGTTAATCGGAATTACTGGGCGTAAAGCGTGCGCAGGCGGTTTGCTAAGACCGATGTGAAATCCCCGGGCTCAACCTGGGAACTGCATTGGTGACTGGCAGGCTAGAGTATGGCAGAGGGGGGTAGAATTCCACGTGTAGCAGTGAAATGCGTAGAGATGTGGAGGAATACCGATGGCGAAGGCAGCCCCCTGGGCCAATACTGACGCTCATGCACGAAAGCGTGGGGAGCAAACAGGATTAGATACCCTGGTAGTCCACGCCCTAAACGATGTCAACTAGTTGTTGGGGATTCATTTCCTTAGTAACGTAGCTAACGCGTGAAGTTGACCGCCTGGGGAGTACGGTCGCAAGATTAAAACTCAAAGGAATTGACGGGGACCCGCACAAGCGGTGGATGATGTGGATTAATTCGATGCAACGCGAAAAACCTTACCTACCCTTGACATGGTCGGAATCCCGCTGAGAGGTGGGAGTGCTCGAAAGAGAACCGGCGCACAGGTGCTGCATGGCTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTTGTCCTTAGTTGCTACGCAAGAGCACTCTAAGGAGACTGCCGGTGACAAACCGGAGGAAGGTGGGGATGACGTCAAGTCCTCATGGCCCTTATGGGTAGGGCTTCACACGTCATACAATGGTCGGAACAGAGGGTTGCCAACCCGCGAGGGGGAGCTAATCCCAGAAAACCGATCGTAGTCCGGATTGCACTCTGCAACTCGAGTGCATGAAGCTGGAATCGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTCACACCATGGGAGTGGGTTTTACCAGAAGTGGCTAGTCTAACCGCAAGGAGGACGGTCACCACGGTAGGATTCATGACTGGGGTGAAGTCGTAACAAGGTAGCCGTATCGGAAGGTGCGGCTGGATCACCTCCTTTCCAGAGCTATCTCGCAAAGTTGAGCGCTCACGCTTATCGGCTGTAAATTTAAAGACAGACTCAGGGGTCTGTAGCTCAGTCGGTTAGAGCACCGTCTTGATAAGGCGGGGGTCGTTGGTTCGAATCCAACCAGACCCACCATTGTCTG
>11458037
GACGAACGCTGGCGGCGTGCCTAACACATGCAAGTCGAACGGTTTCGAAGATCGGACTTCGAATTTCGAATTTCGATCATCGAGATAGTGGCGGACGGGTGAGTAACGCGTGGGTAACCTACCCATAAAGCCGGGACAACCCTTGGAAACGAGGGCTAATACCGGATAAGCTTGAGAAGTGGCATCACTTTTTAAGGAAAGGTGGCCGATGAGAATGCTGCCGATTATGGATGGACCCGCGTCTGATTAGCTGGTTGGTGGGGTAAAGGCCTACCAAGGCGACGATCAGTAGCCGGCCTGAGAGGGTGAACGGCCACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATCTTCCGCAATGGACGAAAGTCTGACGGAGCAACGCCGCGTGTATGATGAAGGTTTTCGGATTGTAAAGTACTGTCTATGGGGAAGAATGGTGTGCTTGAGAATATTAAGTACAAATGACGGTACCCAAGGAGGAAGCCCCGGCTAACTACGTGCCAGCAGCCGCGGTAATACGTAGGGGGCAAGCGTTGTCCGGAATTATTGGGCGTAAAGGGCGCGTAGGCGGATAGTTAAGTCCGGTGTGAAAGATCAGGGCTCAACCCTGAGAGTGCATCGGAAACTGGGTATCTTGAGGACAGGAGAGGAAAGTGGAATTCCACGTGTAGCGGTGAAATGCGTAGATATGTGGAGGAACACCAGTGGCGAAGGCGACTTTCTGGACTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGGATTAGATACCCTGGTAGTCCACGCTGTAAACGATGAGTGCTAGGTGTAGAGGGTATCGACCCCTTCTGTGCCGCAGTTAACACAATAAGCACTCCGCCTGGGGAGTACGGCCGCAAGGTTGAAACTCAAAGGAATTGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGACGCAACGCGAAGAACCTTACCAGGGCTTGACATCCTCTGAACTTGCTGGAAACAGGAAGGTGCCCTTCGGGGAGCAGAGAGACAGGTGGTGCATGGTTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAATCCCGCAACGAGCGCAACCCCTGTATTTAGTTGCTAACGCGTAGAGGCGAGCACTCTGGATAGACTGCCGGTGATAAACCGGAGGAAGGTGGGGATGACGTCAAATCATCATGCCCCTTATGTTCTGGGCTACACACGTGCTACAATGGCCGGTACAGACGGAAGCGAAGCCGCGAGGCGGAGCAAATCCGAGAAAGCCGGTCTCAGTTCGGATTGCAGGCTGCAACTCGCCTGCATGAAGTCGGAATCGCTAGTAATCGCAGGTCAGCATACTGCGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCACGAAAGTCTGCAACACCCGAAGCCGGTGAGGTAACCGACTCGAGATTCGAGGCTCGAAGTTCGAGGATCGAAGTGTAAGCGAAATTAATAAGTCTTAGTAAAGCTAAAAAGCATTAAGACCGATAAGATGATCTTGCAATCGAACATCGAACATCGAATTTCGAACCTCGAGTTGGAGCTAGCCGTCGAAGGTGGGGCCGATAATTGGGGTG
>11469739
AGAGTTTGATCCTGGCTCAGGATGAACGCTGGCGGCGTGCCTAACACATGCAAGTCGAACGAGAAGCTAACTTCTGATTCCTTCGGGATGATGAGGTTAGCAGAAAGTGGCGAACGGGTGAGTAACGCGTGGGTAATCTACCCTGTAAGTGGGGGATAACCCTCCGAAAGGAGGGCTAATACCGCATAATATCTTTATCCCAAAAGAGGTAAAGATTAAAGATGGCCTCTATACTATGCTATCGCTTCAGGATGAGTCCGCGTCCTATTAGTTAGTTGGTGGGGTAATGGCCTACCAAGACGACAATGGGTAGCCGGTCTGAGAGGATGTACGGCCACACTGGGACTGAGATACGGCCCAGACTCCTACGGGAGACAGCAGTGGGGAATATTGCGCAATGGGGGAAACCCTGACGCAGCGACGCCGCGTGGATGATGAAGGCCCTTGGGTTGTAAAATCCTGTTCTGGGGGAAGAAAGCTTAAAGGTCCAATAAACCCTTAAGCCTGACGGTACCCCAAGAGAAAGCTCCGGCTAATTATGTGCCAGCAGCCGCGGTAATACATAAGGAGCAAGCGTTATCCGGAATTATTGGGCGTAAAGAGCTCGTAGGCGGTCTTAAAAGTCAGTTGTGAAATTATCAGGCTCAACCTGATAAGGTCATCTGAAACTCTAAGACTTGAGGTTAGAAGAGGAAAGTGGAATTCCCGGTGTAGCGGTGAAATGCGTAGATATCGGGAGGAACACCAGTGGCGAAGGCGGCTTTCTGGTCTATCTCTGACGCTGAGGAGCGAAAGCTAGGGGAGCAAACGGGATTAGATACCCCGGTAGTCCTAGCTGTAAACGATGGATACTAGGTGTGGGAGGTATCGACCCCTTCTGTGCCGTAGCTAACGCATTAAGTATCCCGCCTGGGGAGTACGGTCGCAAGGCTGAAACTCAAAGGAATTGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGACGCAACGCGAAGAACCTTACCGGGACTTGACATTATCTTGCCCGTCTAAGAAATTAGATCTTCTTCCTTTGGAAGACAGGATAACAGGTGGTGCATGGTTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCCCACAACGAGCGCAACCCTTGTGCTTAGTTGCTAACTTGTTTTACAAGTGCACTCTAGGCAGACTGCCGCAGATAATGCGGAGGAAGGTGGGGATGACGTCAAATCATCATGCCCCTTACGTCCCGGGCTACACACGTGCTACAATGGCCTGTACAGAGGGTAGCGAAAGAGCGATCTTAAGCCAATCCCAAAAAGCAGGCCCCAGTTCGGATTGGAGGCTGCAACTCGCCTCCATGAAGTAGGAATCGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCACGAAAGTTGGCGATACCTGAAGTTACTAGGCTAACCTGGCACTCAACTAAGTTCACTAACTTATTTGCTTAAAATAAGGCTTAATGTGCTTAGTTGAGTGCCGGGAGGCAGGTACCGAAGGTATGGCTGGCGATTGGGGTGAAGTCGTAACAAGGTGGAAA
>11469752
AGAGTTTGATCCTGGCTCAGGATGAACGCTGGCGGCGTGCCTAATACATGCAAGTCGAGCGGCAGCGAGTTCCTCACCGAGGTTCGGAACAGTTGACAGTAAACAGTTGACAGTAAACAGTAACTTCAGAAATGAAGCGGACTGTGAACTGTTTACTGTAACCTGTTAGCTATTATTTCGAGCTTTAGTGAGGAATGTCGGCGAGCGGCGGACGGCTGAGTAACGCGTAGGAACGTACCCCAAACTGAGGGATAAGCACCAGAAATGGTGTCTAATACCGCATATGGCCCAGCACCTTTTTTAATCAACCACGACCCTAAAATCGTGAATAATTGGTAGGAAAAGGTGTTGGGTTAAAGCTTCGGCGGTTTGGGAACGGCCTGCGTATGATTAGCTTGTTGGTGAGGTAAAAGCTCACCAAGGCGACGATCATTAGCTGGTCTGAGAGGATGATCAGCCAGACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTAGGGAATCTTCCACAATGGGCGAAAGCCTGATGGAGCAACGCCGTGTGCAGGATGAAAGCCTTCGGGTCGTAAACTGCTTTTATATGTGAAGACTTCGACGGTAGCATATGAATAAGGATCGGCTAACTCCGTGCCAGCAGCCGCGGTCATACGGAGGATCCAAGCGTTATCCGGAATTACTGGGCGTAAAGAGTTGCGTAGGTGGCATAGTAAGTTGGTAGTGAAATTGTGTGGCTCAACCATACACCCATTACTAAAACTGCTAAGCTAGAGTATATGAGAGGTAGCTGGAATTCCTAGTGTAGGAGTGAAATCCGTANATATTAGGAGGAACACCGATGGCGTAGGCAGGCTACTGGCATATTACTGACACTAAGGCACGAAAGCGTGGGGAGCGAACGGGATTAGATACCCCGGTAGTCCACGCTGTAAACGATGGATGCTAGCTGTTATGAGTATCGACCCTTGTAGTAGCGAAGCTAACGCGTTAAGCATCCCGCCTGTGGAGTACGAGCGCAAGCTTAAAACATAAAGGAATTGACGGGGACCCGCACAAGCGGTGGAGCGTGTTGTTTAATTCGATGATAAGCGAAGAACCTTACCAAGGCTTGACATCCCTGGAATTTCTCCGAAAGGAGAGAGTGCCTTCGGGAATCAGGTGACAGGTGATGCATGGCCGTCGTCAGCTCGTGTCGTGAGATGTTTGGTTAAGTCCATTAACGAGCGCAACCCTTGTAAATAGTTGGATTTTTCTATTTAGACTGCCTCGGTAACGGGGAGGAAGGAGGGGATGATGTCAGGTCAGTATTTCTCTTACGCCTTGGGCTACAAACACGCTACAATGGCCGGTACAAAGGGCAGCCAACCCGCGAGGGGGAGCAAATCCCATCAAAGCCGGTCTCAGTTCGGATAGCAGGCTGAAATTCGCCTGCTTGAAGTCGGAATCGCTAGTAACGGTGAGTCAGCTATATTACCGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTCAAGGCATGAAAGTCATCAATACCTGACGTCTGGATTTATTCTGGCCTAAGGTAGGGGCGATGATTGGGCCTAAGTCGTAACAAGGTAA
>11460523
AGAGTTTGATCCTGGCTCAGAACGAACGCTGGCGGCGTGCTTAACACATGCAAGTCGAACGCGAAATCGGGCACTCAATTTTGCTTTTCAAACATTAACTGATGAAACGACCAGAGAGATTGTTCCAGTTTAAAGAGTGAAAAGCAGGCTTGAGTGCCTGAGAGTAGAGTGGCGCACGGGTGAGTAACGCGTAAATAATCTACCCCTGCATCTGGGATAACCCACCGAAAGGTGAGCTAATACCGGATACGTTCTTTTAACCGCGAGGTTTTAAGAAGAAAGGTGGCCTCTGATATAAGCTACTGTGCGGGGAGGAGTTTGCGTACCATTAGCTAGTTGGTAGGGTAATGGCCTACCAAGGCATCGATGGTTAGCGGGTCTGAGAGGATGATCCGCCACACTGGAACTGGAACACGGACCAGACTCCTACGGGAGGCAGCAGTGAGGAATATTGCGCAATGGGGGCAACCCTGACGCAGCGACGCCGCGTGGATGATGAAGGCCTTCGGGTCGTAAAATCCTGTCAGATGGAAAGAAGTGTTATATGGATAATACCTGTATAGCTTGACGGTACCATCAAAGGAAGCACCGGCTAACTCCGTGCCAGCAGCCGCGGTAATACGGAGGGTGCAAGCGTTGTTCGGAATTACTGGGCGTAAAGCGCGCGTAGGCGGTCTGTTATGTCAGATGTGAAAGTCCACGGCTCAACCGTGGAAGTGCATTTGAAACTGACAGACTTGAGTACTGGAGGGGGTGGTGGAATTCCCGGTGTAGAGGTGAAATTCGTAGATATCGGGAGGAATACCGGTGGCGAAGGCGACCACCTGGCCAGATACTGACGCTGAGGTGCGAAAGCGTGGGGAGCAAACAGGATTAGATACCCTGGTAGTCCACGCCGTAAACGATGTCAACTAGGTGTTGGGATGGTTAATCGTCTCATTGCCGGAGCTAACGCATTAAGTTGACCGCCTGGGGAGTACGGTCGCAAGATTAAAACTCAAAGGAATTGACGGGGGCCCGCACAAGCGGTGGAGTATGTGGTTTAATTCGACGCAACGCGCAGAACCTTACCTGGTCTTGACATCCCGAGAATCTCAAGGAAACTTGAGAGTGCCTCTTGAGGAACTCGGTGACAGGTGCTGCATGGCTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTTGTCTTTAGTTGCCATCATTAAGTTGGGCACTCTAAAGAGACTGCCGGTGTCAAACCGGAGGAAGGTGGGGATGACGTCAAGTCCTCATGGCCTTTATGACCAGGGCTACACACGTACTACAATGGCATAGACAAAGGGCAGCGACATCGCGAGGTGAAGCGAATCCCATAAACCATGTCTCAGTCCGGATTGGAGTCTGCAACTCGACTCCATGAAGTTGGAATCGCTAGTAATCGTAGATCAGCATGCTACGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCACGGGAGTTGGTTGTACCAGAAGCAGTTGAGCGAACTATTCGTAGACGCAGGCTGCCAAGGTATGATTGGTAACTGGGGTGAAGTCGTAACAAGGTAACC
>11460543
TGGTTTGATCCTGGCTCAGGACAAACGCTGGCGGCGTGCCTAACACATGCAAGTCGAACGAGAAGCCAGCTTTTGATTCCTTCGGGATGAGAAAGCAGGTAGAAAGTGGCGAACGGGTGAGTAACGCGTGGGTAATCTACCCTGTAAGTAGGGGATAACCCTCTGAAAAGAGGGCTAATACCGCATAATATCTTTACCCCATAAGAAGTAAAGATTAAAGATGGCCTCTGTATATGCTATCGCTTCAGGATGAGCCCGCGTCCTATTAGTTAGTTGGTAAGGTAATGGCTTACCAAGACCACGATGGGTAGCCGGTCTGAGAGGATGTACGGCCACACTGGGACTGAGATACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATATTGCGCAATGGGGGAAACCCTGACGCAGCGACGCCGCGTGGATGATGAAGGCCTTCGGGTTGTAAAATCCTGTTTTGGGGGACGAAACCTTAAGGGTCCAATAAACCCTTAAATTGACGGTACCCCAAGAGAAAGCTCCGGCTAATTATGTGCCAGCAGCCGCGGTAATACATAAGGAGCAAGCGTTGTCCGGAATTATTGGGCGTAAAGAGTTCGTAGGCGGTCTTAAAAGTCAGGTGTGAAATTATCAGGCTTAACCTGATACGGTCATCTGAAACTTTAAGACTTGAGGTTAGGAGAGGAAAGTGGAATTCCCGGTGTAGCGGTGAAATGCGTAGATATCGGGAGGAACACCAGTGGCGAAGGCGGCTTTCTGGCCTAACTCTGACGCTGAGGAACGAAAGCTAGGGGAGCAAACGGGATTAGATACCCCGGTAGTCCTAGCTGTAAACGATGGATACTAGGTGTGGGAGGTATCGACCCCTTCTGTGCCGWCACTAACGCATTAAGTATCCCGCCTGGGGAGTACGGTCGCAAGGCTAAAACTCAAAGGAATTGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGACGCAACGCGAAGAACCTTACCGGGGCTTGACATTGTCTTGCCCGTTTAAGAAATTAAATTTTCTTCCCTTTTAGGGAAGACAAGATAACAGGTGGTGCATGGTTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCCCACAACGAGCGCAACCCTTATTCTTAGTTGCTAGTTTGTTTACAAACGCACTCTAAAGAGACTGCCGCAGATAATGCGGAGGAAGGTGGGGATGACGTCAAATCATCATGCCCCTTACGTCCCGGGCTACACACGTGCTACAATGGCCTGTACAGAGGGTAGCGAAAGAGCGATCTCAAGCTAATCCCTTAAAACAGGTCTCAGTTCGGATTGGAGGCTGCAACTCGCCTCCATGAAGTCGGAATCGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCATGAAAGTTGGCGATACCTGAAGTTACTGTGCTAACCCGGCACTCAACTAAGTACATTAAGTCTTATTTTAAGCTATTGTATTTAGTTGAGTGCCGGGAGGCAGGTACCTAAGGTATGGCTAGCGATTGGGGTGAAGTCGTAACAAGGTAGCCG
>11480235
TGGTTTGATCCTGGCTCAGGATTAACGCTGGCGGCGCGCCTTATACATGCAAGTCGAACGAGCCTTGTGCTTCGCACAAGGAAATTCCAAGCACCAAGCACCAAATCTCAAACAAATCCCAATGACCAAAATTCCAAAAACCTAAACATTTTAAATGTTTAGAATTTGGAAAATTGGAATTTGGAATTTATTTGTTATTTGGAATTTATGATTTGGGATTTTCTCGCGCGGAGANCNTNAGTGGCGAACGGGTGAGTAATACGTTGGTATCTACCCCAAAGTAGAGAATAAGCCCGAGAAATCGGGGTTAATACTCTATGTGTTCGAAAGAACAAAGACTTCGGTTGCTTTGGGAAGAACCTGCGGCCTATCAGCTTGTTGGTAAGGTAACGGCTTACCAAGGCTTTGACGGGTAGCTGGTCTGGGAAGACGACCAGCCACAATGGGACTTAGACACGGCCCATACTCCTACGGGAGGCAGCAGTAGGGAATCTTCGGCAATGCCCGAAAGGTGACCGAGCGACGCCGCGTAGAGGAAGAAGATCTTTGGATTGTAAACTCTTTTTCTCCTAGACAAAGTTCTGATTGTATAGGAGGAATAAGGGGTTTCTAAACTCGTGCCAGCAGAAGCGGTAATACGAGTGCCCCAAGCGTTATCCGGAATCATTGGGCGTAGAGCGTTGTATAGGTGGTTTAAAAAGTCCAAAATTAAATCTTTAGGCTCAACCTAAAATCTGTTTTGGAAACTTTTAGACTTGAATAAAATCGACGSGAGTGGAACTTCCAGAGTAGGGGTTACATCCGTTGATACTGGAAGGAACGCCGAAGGCGAAAGCAACTCGCGAGATTTTATTGACGCCGCGTACACGAAAGCGTGGGGAGCGAAAAGTATTAGATACACTTGTAGTCCACGCCGTAAACTATGGATACTAGCAATTTGAAGCTTCGACCCTTCAAGTTGCGGACTAACGCGTTAAGTATCTCGCCTGGGAAGTACGGCCGCAAGGCTAAAACTCAAAGGAATAGACGGGGGCCCGCACAAGCGGTGGAGCATGTGGTTTAATTCGACGATAAGCGTGGAACCTTACCAGGGCTTAGACGTACAGAGAATTCCTTGGAAACAAGGAAGTGCTTCGGGAACTCTGTACTCAGGTACTGCATGGCTGTCGTCAGTATGTACTGTGAAGCACTCCCTTAATTGGGGCAACATACGCAACCCCTATCCTAAGTTAGAAATGTCTTAGGAAACCGCTTCGATTCATCGGAGAGGAAGATGGGGACGACGTCAAGTCAGCATGGTCCTTGATGTCCTGGGCGACACACGTGCTACAATGGCTAGTATAACGGGATGCGTAGGTGCGAACCGAAGCTAATCCTTAAAAAACTAGTCTAAGTTCGGATTGAAGTCTGCAACTCGACTTCATGAAGCCGGAATCGCTAGTAACCGCAAATCAGCCACGTTGCGGTGAATACGTTCTCGGGCCTTGTACTCACTGCCCGTCACGTCAAAAAAGTCGGTAATACCCGAAGCACCCTTTTAAAGGGTTCTAAGGTAGGACCGATGATTGGGACGAAGTCGTAACAAGGTAGCCG
>11480408
AATTTAGCGGCCGCGAATTCGCCCTTGAGTTTGATCCTGGCTCAGGACGAACGCTGGCGGCGTGCTTAACACATGCAAGTCGAACGGGGATATCCGAGCGGAAGGTTTCGGCCGGAAGGTTGGGTATTCGAGTGGCGGACGGGTGAGTAACGCGTGAGCAATCTGTCCCGGACAGGGGGATAACACTTGGAAACAGGTGCTAATACCGCATAAGACCACAGCATCGCATGGTGCAGGGGTAAAAGGAGCGATCCGGTCTGGGGTGAGCTCGCGTCCGATTAGATAGTTGGTGAGGTAACGGCCCACCAAGTCAACGATCGGTAGCCGACCTGAGAGGGTGATCGGCCACATTGGAACTGAGAGACGGTCCAAACTCCTACGGGAGGCAGCAGTGGGGAATATTGGGCAATGGGCGAAAGCCTGACCCAGCAACGCCGCGTGAGTGAAGAAGGCCTTCGGGTTGTAAAGCTCTGTTATGCGAGACGAAGGAAGTGACGGTATCGCATAAGGAAGCCCCGGCTAACTACGTGCCAGCAGCCGCGGTAATACGTAGGGGGCGAGCGTTGTCCGGAATGACTGGGCGTAAAGGGCGTGTAGGCGGCCGTTTAAGTATGGAGTGAAAGTCCATTTTTCAAGGATGGAATTGCTTTGTAGACTGGATGGCTTGAGTGCGGAAGAGGTAAGTGGAATTCCCAGTGTAGCGGTGAAATGCGTAGAGATTGGGAGGAACACCAGTGGCGAAGGCGACTTACTGGGCCGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCGAACAGGATTAGATACCCTGGTAGTCCACGCGGTAAACGATGAATGCTAGGTGTTGCGGGTATCGACCCCTGCAGTGCCGGAGTAAACACAATAAGCATTCCGCCTGGGGAGTACGGCCGCAAGGTTGAAACTCAAGGGAATTGACGGGGGCCCGCACAAGCAGCGGAGCATGTTGTTTAATTCGAAGCAACGCGAAGAACCTTACCAGGTCTTGACATCCAGTTAAGCTCATAGAGATATGAGGTCCCTTCGGGGGAACTGAGACAGGTGGTGCATGGTTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTTATGGTCAGTTACTAACGCGTGAAGGCGAGGACTCTGACGAGACTGCCGGGGACAACTCGGAGGAAGGTGGGGACGACGTCAAATCATCATGCCCCTTATGACCTGGGCTACAAACGTGCTACAATGGTGACTACAAAGAGGAGCGAGACTGTAAAGTGGAGCGGATCTCAAAAAAGTCATCCCAGTTCGGATTGTGGGCTGCAACCCGCCCACATGAAGTTGGAGTTGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCATGGGAGTTGGGAGCACCCGAAGTCAGTGAGGTAACCGGAAGGAGCCAGCTGCCGAAGGTGAGACCGATGACTGGGGTGAAGTCGTAACAAGGTAGCCGTATCGGAAGGTGCGGCTGGATCACCTCCTTAAGGGCGAATTCGTTTAAACCTGCAGGACTAG
"""

test_seq = """>s1 (11472384)
AGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCATGCCTTACACATGCAAGTCGAACGGCAGCACGGGGGCAACCCTGGTGGCGAGTGGCGAACGGGTGAGTAATACATCGGAACGTGTCCTGTAGTGGGGGATAGCCCGGCGAAAGCCGGATTAATACCGCATACGCTCTACGGAGGAAAGGGGGGGATCTTAGGACCTCCCGCTACAGGGGCGGCCGATGGCAGATTAGCTAGTTGGTGGGGTAAAGGCCTACCAAGGCGACGATCTGTAGCTGGTCTGAGAGGACGACCAGCCACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATTTTGGACAATGGGGGCAACCCTGATCCAGCAATGCCGCGTGTGTGAAGAAGGCCTTCGGGTTGTAAAGCACTTTTGTCCGGAAAGAAAACGCCGTGGTTAATACCCGTGGCGGATGACGGTACCGGAAGAATAAGCACCGGCTAACTACGTGCCAGCAGCCGCGGTAATACGTAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGTGCGCAGGCGGTCCGCTAAGACAGATGTGAAATCCCCGGGCTTAACCTGGGAACTGCATTTGTGACTGGCGGGCTAGAGTATGGCAGAGGGGGGTAGAATTCCACGTGTAGCAGTGAAATGCGTAGAGATGTGGAGGAATACCGATGGCGAAGGCAGCCCCCTGGGCCAATACTGACGCTCATGCACGAAAGCGTGGGGAGCAAACAGGATTAGATACCCTGGTAGTCCACGCCCTAAACGATGTCAACTAGTTGTCGGGTCTTCATTGACTTGGTAACGTAGCTAACGCGTGAAGTTGACCGCCTGGGGAGTACGGTCGCAAGATTAAAACTCAAAGGAATTGACGGGGACCCGCACAAGCGGTGGATGATGTGGATTAATTCGATGCAACGCGAAAAACCTTACCTACCCTTGACATGTATGGAATCCTGCTGAGAGGTGGGAGTGCCCGAAAGGGAGCCATAACACAGGTGCTGCATGGCTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCCCGCAACGAGCGCAACCCTTGTCCCTAGTTGCTACGCAAGAGCACTCTAGGGAGACTGCCGGTGACAAACCGGAGGAAGGTGGGGATGACGTCAAGTCCTCATGGCCCTTATGGGTAGGGCTTCACACGTCATACAATGGTCGGAACAGAGGGTCGCCAACCCGCGAGGGGGAGCCAATCCCAGAAAACCGATCGTAGTCCGGATCGCACTCTGCAACTCGAGTGCGTGAAGCTGGAATCGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTCACACCATGGGAGTGGGTTTTACCAGAAGTGGCTAGTCTAACCGCAAGGAGGACGGTCACCACGGTAGGATTCATGACTGGGGTGAAGTCGTAACAAGGTAGCCGTATCGGAAGGTGCGGCTGGATCACCTCCTTTCTCGAGCGAACGTGTCGAACGTTGAGCGCTCACGCTTATCGGCTGTGAAATTAGGACAGTAAGTCAGACAGACTGAGGGGTCTGTAGCTCAGTCGGTTAGAGCACCGTCTTGATAAGGCGGGGGTCGATGGTTCGAATCCATCCAGACCCACCATTGTCT
"""

in_aln1 = """>a1
AAACCTTT----TTTTAAATTCCGAAGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCATGCCTTACACATGCAAGTCGAACGGCAGCACGGGGGCAACCCTGGTGGCGAGTGGCGAACGGGTGAGTAATACATCGGAACGTGTCCTGTAGTGGGGGATAGCCCGGCGAAAGCCGGATTAATACCGCATACGCTCTACGGAGGAAAGGGGGGGATCTTAGGACCTCCCGCTACAGGGGCGGCCGATGGCAGATTAGCTAGTTGGTGGGGTAAAGGCCTACCAAGGCGACGATCTGTAGCTGGTCTGAGAGGACGACCAGCCACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATTTTGGACAATGGGGGCAACCCTGATCCAGCAATGCCGCGTGTGTGAAGAAGGCCTTC
>a2
AAACCTTT----TTTTAAATTCCGCAGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCATGCCTTACACATGCAAGTCGAACGGCAGCACGGGGGCAACCCTGGTGGCGAGTGGCGAACGGGTGAGTAATACATCGGAACGTGTCCTGTAGTGGGGGATAGCCCGGCGAAAGCCGGATTAATACCGCATACGCTCTACGGAGGAAAGGGGGGGATCTTAGGACCTCCCGCTACAGGGGCGGCCGATGGCAGATTAGCTAGTTGGTGGGGTAAAGGCCTACCAAGGCGACGATCTGTAGCTGGTCTGAGAGGACGACCAGCCACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATTTTGGACAATGGGGGCAACCCTGATCCAGCAATGCCGCGTGTGTGAAGAAGGCCTTC
>a3
AAACCTTT----TTTTAAATTCCGGAGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCATGCCTTACACATGCAAGTCGAACGGCAGCACGGGGGCAACCCTGGTGGCGAGTGGCGAACGGGTGAGTAATACATCGGAACGTGTCCTGTAGTGGGGGATAGCCCGGCGAAAGCCGGATTAATACCGCATACGCTCTACGGAGGAAAGGGGGGGATCTTAGGACCTCCCGCTACAGGGGCGGCCGATGGCAGATTAGCTAGTTGGTGGGGTAAAGGCCTACCAAGGCGACGATCTGTAGCTGGTCTGAGAGGACGACCAGCCACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATTTTGGACAATGGGGGCAACCCTGATCCAGCAATGCCGCGTGTGTGAAGAAGGCCTTC
>a4
AAACCTTT----TTTTAAATTCCGTAGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCATGCCTTACACATGCAAGTCGAACGGCAGCACGGGGGCAACCCTGGTGGCGAGTGGCGAACGGGTGAGTAATACATCGGAACGTGTCCTGTAGTGGGGGATAGCCCGGCGAAAGCCGGATTAATACCGCATACGCTCTACGGAGGAAAGGGGGGGATCTTAGGACCTCCCGCTACAGGGGCGGCCGATGGCAGATTAGCTAGTTGGTGGGGTAAAGGCCTACCAAGGCGACGATCTGTAGCTGGTCTGAGAGGACGACCAGCCACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATTTTGGACAATGGGGGCAACCCTGATCCAGCAATGCCGCGTGTGTGAAGAAGGCCTTC
"""


if __name__ == "__main__":
    main()
