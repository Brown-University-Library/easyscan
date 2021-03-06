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
            Called by models.RequestViewPostHelper.transfer_data().
            Future: will likely be triggered by a queued-job. """
        self.ensure_empty_dir()
        filename_datestring = self.make_filename_datestring( datetime_object )
        data_filename = self.save_data_file( filename_datestring, data_string )
        count_filename = self.save_count_file( filename_datestring )
        log.debug( u'in lib.magic_bus.Prepper.make_data_files(); data_filename, `%s`; count_filename, `%s`' % (data_filename, count_filename) )
        return ( data_filename, count_filename )

    def ensure_empty_dir( self ):
        """ Empties source-transfer directory.
            Called by make_data_files() """
        filelist = os.listdir( self.source_transfer_dir_path )
        for filename in filelist:
            delete_path = u'%s/%s' % ( self.source_transfer_dir_path, filename )
            os.remove( delete_path )
        return

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
        os.chmod( filepath, 0o664 )
        return filename

    def save_count_file( self, filename_datestring ):
        """ Saves count file.
            Called by make_data_files() """
        filename = u'%s_%s%s' % ( self.filename_prefix, filename_datestring, self.count_file_suffix )
        filepath = u'%s/%s' % ( self.source_transfer_dir_path, filename )
        with open( filepath, u'w' ) as f:
            f.write( '1\n' )
        os.chmod( filepath, 0o664 )
        return filename


class Sender( object ):
    """ Container for file-transfer code. """

    def __init__( self ):
        self.SERVER = unicode( os.environ[u'EZSCAN__REMOTE_SERVER'] )
        self.USERNAME = unicode( os.environ[u'EZSCAN__TRANSFER_USERNAME'] )
        self.PASSWORD = unicode( os.environ[u'EZSCAN__TRANSFER_PASSWORD'] )
        self.LOCAL_DIR = unicode( os.environ[u'EZSCAN__SOURCE_TRANSFER_DIR_PATH'] )
        self.REMOTE_DATA_DIR = unicode( os.environ[u'EZSCAN__REMOTE_TRANSFER_DATA_DIR_PATH'] )
        self.REMOTE_COUNT_DIR = unicode( os.environ[u'EZSCAN__REMOTE_TRANSFER_COUNT_DIR_PATH'] )

    def transfer_files( self, data_filename, count_filename ):
        """ Transfers data-file and count-file.
            Called by models.RequestViewPostHelper.transfer_data()
            Future: will likely be triggered by a queued-job. """
        ( data_source_fp, data_remote_fp, count_source_fp, count_remote_fp ) = self.build_filepaths( data_filename, count_filename )
        ssh = self.setup_ssh()
        self.run_sftp( ssh, data_source_fp, data_remote_fp, count_source_fp, count_remote_fp )
        ssh.close()
        log.debug( u'in lib.magic_bus.Sender.transfer_files(); files transferred' )
        return

    def build_filepaths( self, data_filename, count_filename ):
        """ Builds and returns tuple of source and remote filepaths.
            Called by transfer_files() """
        data_source_fp = '%s/%s' % ( self.LOCAL_DIR, data_filename )
        data_remote_fp = '%s/%s' % ( self.REMOTE_DATA_DIR, data_filename )
        count_source_fp = '%s/%s' % ( self.LOCAL_DIR, count_filename )
        count_remote_fp = '%s/%s' % ( self.REMOTE_COUNT_DIR, count_filename )
        log.debug( 'data_source_fp, ```%s```' % data_source_fp )
        log.debug( 'data_remote_fp, ```%s```' % data_remote_fp )
        log.debug( 'count_source_fp, ```%s```' % count_source_fp )
        log.debug( 'count_remote_fp, ```%s```' % count_remote_fp )
        return ( data_source_fp, data_remote_fp, count_source_fp, count_remote_fp )

    def setup_ssh( self ):
        """ Sets up and returns ssh object.
            Called by transfer_files() """
        ssh = paramiko.SSHClient()
        log.debug( u'in lib.magic_bus.Sender.setup_ssh(); ssh client instantiated' )
        ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        log.debug( u'in lib.magic_bus.Sender.setup_ssh(); ssh missing key policy set' )
        ssh.connect( self.SERVER, username=self.USERNAME, password=self.PASSWORD )
        log.debug( u'in lib.magic_bus.Sender.setup_ssh(); ssh connection made' )
        return ssh

    def run_sftp( self, ssh, data_source_fp, data_remote_fp, count_source_fp, count_remote_fp ):
        """ Instantiates and runs sftp transfer.
            Called by transfer_files() """
        sftp = ssh.open_sftp()
        sftp.put( data_source_fp, data_remote_fp )
        sftp.put( count_source_fp, count_remote_fp )
        sftp.close()
        log.debug( u'in lib.magic_bus.Sender.run_sftp(); sftp executed' )
        return
