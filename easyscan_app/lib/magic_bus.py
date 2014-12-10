# -*- coding: utf-8 -*-

""" Transports scan-request files to LAS location. """

import logging, os
import paramiko


log = logging.getLogger(__name__)


class Prepper( object ):
    """ Container for data-preparation code. """

    def __init__( self ):
        self.source_transfer_dir_path = unicode( os.environ[u'EZSCAN__SOURCE_TRANSFER_DIR_PATH'] )
        self.filename_prefix = u'REQ-PARSED'
        self.data_file_suffix = u'.dat'
        self.count_file_suffix = u'.cnt'

    def make_data_files( self, datetime_object, data_string ):
        """ Creates data files that will be transferred to remote server.
            Job triggered by (we'll see). """
        log.debug( u'in magic_bus.Prepper.make_data_files(); starting' )
        self.ensure_empty_dir()
        log.debug( u'in magic_bus.Prepper.make_data_files(); dir is empty' )
        filename_datestring = self.make_filename_datestring( datetime_object )
        log.debug( u'in magic_bus.Prepper.make_data_files(); filename_datestring made' )
        data_filename = self.save_data_file( filename_datestring, data_string )
        log.debug( u'in magic_bus.Prepper.make_data_files(); data_filename made' )
        count_filename = self.save_count_file( filename_datestring )
        log.debug( u'in magic_bus.Prepper.make_data_files(); count_filename made; returning' )
        return ( data_filename, count_filename )

    def ensure_empty_dir( self ):
        """ Raises exception if directory is not empty.
            Called by make_data_files() """
        if not os.listdir( self.source_transfer_dir_path ) == []:
            raise Exception( u'Source path `%s` must be empty.' % self.source_transfer_dir_path )

    def make_filename_datestring( self, datetime_object ):
        """ Returns formatted date string.
            Example returned format, `2014-12-08T15:40:59`.
            Called by make_data_files() """
        utf8_date_string = datetime_object.strftime( u'%Y-%m-%dT%H:%M:%S' )  # temp: REQ-PARSED_2014-09-29T13:10:02.dat
        date_string = utf8_date_string.decode( u'utf-8' )
        return date_string

    def save_data_file( self, filename_datestring, data_string ):
        """ Saves data file.
            Called by make_data_files() """
        filename = u'%s_%s%s' % ( self.filename_prefix, filename_datestring, self.data_file_suffix )
        filepath = u'%s/%s' % ( self.source_transfer_dir_path, filename )
        buffer1 = data_string.strip()
        buffer2 = buffer1 + u'\n'
        utf8_data_string = buffer2.encode( u'utf-8', u'replace' )
        with open( filepath, u'w' ) as f:
            f.write( utf8_data_string )
        return filepath

    def save_count_file( self, filename_datestring ):
        """ Saves count file.
            Called by make_data_files() """
        filename = u'%s_%s%s' % ( self.filename_prefix, filename_datestring, self.count_file_suffix )
        filepath = u'%s/%s' % ( self.source_transfer_dir_path, filename )
        with open( filepath, u'w' ) as f:
            f.write( '1\n' )
        return


class Sender( object ):
    """ Container for file-transfer code. """

    def __init__( self ):
        self.SERVER = unicode( os.environ[u'EZSCAN__REMOTE_SERVER'] )
        self.USERNAME = unicode( os.environ[u'EZSCAN__TRANSFER_USERNAME'] )
        self.PASSWORD = unicode( os.environ[u'EZSCAN__TRANSFER_PASSWORD'] )
        self.LOCAL_DIR = unicode( os.environ[u'EZSCAN__SOURCE_TRANSFER_DIR_PATH'] )
        self.REMOTE_DIR = unicode( os.environ[u'EZSCAN__REMOTE_TRANSFER_DIR_PATH'] )

    def transfer_files( self, data_filename, count_filename ):
        """ Transfers data-file and count-file. """
        ( data_source_fp, data_remote_fp, count_source_fp, count_remote_fp ) = self.build_filepaths()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        ssh.load_host_keys( os.path.expanduser(os.path.join(u'~', u'.ssh', u'known_hosts')) )
        ssh.connect( self.SERVER, username=self.USERNAME, password=self.PASSWORD )
        sftp = ssh.open_sftp()
        sftp.put( data_source_fp, data_remote_fp )
        sftp.put( count_source_fp, count_remote_fp )
        sftp.close()
        ssh.close()

    def build_filepaths( self ):
        """ Builds and returns tuple of source and remote filepaths.
            Called by transfer_files() """
        data_source_fp = u'%s/%s' % ( self.LOCAL_DIR, data_filename )
        data_remote_fp = u'%s/%s' % ( self.REMOTE_DIR, data_filename )
        count_source_fp = u'%s/%s' % ( self.LOCAL_DIR, count_filename )
        count_remote_fp = u'%s/%s' % ( self.REMOTE_DIR, count_filename )
        return ( data_source_fp, data_remote_fp, count_source_fp, count_remote_fp )
