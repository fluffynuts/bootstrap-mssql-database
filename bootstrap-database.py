import pypyodbc
import click
import os
import sys
from collections import namedtuple

ConnectionInfo = namedtuple('ConnectionInfo', 'server user password')
BootstrapInfo = namedtuple('BootstrapTuple', 'database user password')
Constants = namedtuple('Constants', 'host instance')
constants = Constants('localhost', '(default)')

class DatabaseBootstrapper:
    """Magick Animal Which doth create databaseth"""
    def __init__(self, connection_info, bootstrap_info, _generate_only, generate):
        self._connection_info = connection_info
        self._bootstrap_info = bootstrap_info
        self._verbose = _generate_only
        self._generate_only = generate
        self._script = []
        self._connection = None

    def run(self):
        """Runs the bootstrapper with the provided options"""
        self._script = []
        self._connect_master()
        self._create_login()
        self._create_database()
        self._close_connection()
        self._connect_app_database()
        self._add_use_database_if_required()
        self._create_app_user()
        self._allow_app_user_connect()
        self._set_app_user_roles()
        self._dump_script_if_required()

    def _add_use_database_if_required(self):
        # required to GO before attempting to use the new database
        self._run_script("GO")
        self._run_script('use [%s]' % self._bootstrap_info.database)

    def _dump_script_if_required(self):
        if not self._generate_only:
            return
        script_file = 'Script-%s.sql' % (self._bootstrap_info.database)
        with open(script_file, mode='w') as stream:
            for line in self._script:
                stream.write("%s\n" % line)
        print('Generated script: %s' % script_file)
        
    def _log(self, message):
        if not self._verbose:
            return
        print(message)

    def _connect_master(self):
        if self._generate_only:
            return
        self._connection = self._connect_to_database('master')

    def _close_connection(self):
        if self._generate_only:
            return
        self._connection.close()

    def _connect_app_database(self):
        if self._generate_only:
            return
        database_name = self._bootstrap_info.database
        self._connection = self._connect_to_database(database_name)

    def _connect_to_database(self, database):
        if self._generate_only:
            return
        if self._connection_info.user == '':
            auth = 'Trusted_Connection=True'
        else:
            auth = 'UID=%s;PWD=%s' % \
            (self._connection_info.user, self._connection_info.password)
        conn_string = 'DRIVER={Sql Server};SERVER=%s;DATABASE=%s;%s' \
             % (self._connection_info.server, database, auth)
        self._log('connecting: %s' % (conn_string))
        return pypyodbc.connect(conn_string)


    def _enquote(self, text):
        return text.replace('\'', '\'\'')

    def _create_app_user(self):
        user = self._bootstrap_info.user
        script = \
'''if not exists (select * from sysusers where name = \'%s\')
begin
    create user %s for login %s with default_schema = dbo
end;''' % (user, user, user)
        self._run_script(script)

    def _allow_app_user_connect(self):
        script = 'grant connect to %s' % (self._bootstrap_info.user)
        self._run_script(script)

    def _set_app_user_roles(self):
        script = 'exec sp_addrolemember N\'%s\', N\'%s\';'
        user = self._bootstrap_info.user
        for role in ['db_datareader', 'db_datawriter', 'db_owner']:
            self._run_script(script % (role, user))

    def _create_database(self):
        db_name = self._bootstrap_info.database
        script = \
'''if not exists(select name from master..sysdatabases where name = \'%s\')
begin
    create database %s
end;
''' % (db_name, db_name)
        self._run_script(script)

    def _create_login(self):
        user = self._enquote(self._bootstrap_info.user)
        password = self._enquote(self._bootstrap_info.password)
        script = \
'''use master;
if not exists (select name from master..syslogins where name = \'%s\')
begin
    create login %s with password = \'%s\';
end;
''' % (user, user, password)
        self._run_script(script)

    def _run_script(self, script):
        if self._generate_only:
            self._script.append(script)
            return
        self._log('run sql: %s' % (script))
        cursor = self._connection.cursor()
        cursor.execute(script)
        self._connection.commit()


@click.command()
@click.option('--host', help='Sql server hostname',
              default=constants.host)
@click.option('--instance', help='Sql Server instance',
              default=constants.instance)
@click.option('--login', help='Admin-level login on Sql Server \
(leave blank for trusted)', default='')
@click.option('--password', help='Admin-level password on Sql Server \
(leave blank for trusted)', default='', hide_input=True)
@click.option('--user-name', prompt='App user to create')
@click.option('--user-password', prompt='Password for app user', 
        hide_input=True, confirmation_prompt=True)
@click.option('--database-name', prompt='Database name to create')
@click.option('--verbose/--quiet', default=False, help='Print debug info')
@click.option('--generate/--live', default=False, help='Generate script or run to live database server (default is run live)')
def main(host, \
        instance, \
        login, \
        password, \
        user_name, \
        user_password, \
        database_name, \
        verbose, \
        generate):
    server = host
    if len(instance) > 0 and instance != constants.instance:
        server = '\\'.join([host, instance])
    connection_info = ConnectionInfo(server, login, password)
    bootstrap_info = BootstrapInfo(database_name, user_name, user_password)
    bootstrapper = DatabaseBootstrapper(
        connection_info,
        bootstrap_info,
        verbose,
        generate)
    bootstrapper.run()

if __name__ == '__main__':
    main()
