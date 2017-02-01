# Bootstrap MSSQL Database

## What this is

A Simple Python script to bootstrap an MSSQL database with a login and associated user who has rights to modify only that database

## What this is not

An example of amazing python code. It works and it's relatively easy to understand, mainly
thanks to the <code>click</code> library

## Requirements

You will need to install the following libraries (probably with <code>pip</code>):
  * click
  * pyodbc

## Usage

Run <code>bootstrap-database.py</code> with <code>--help</code> to get commandline parameters. 
Script may be run with all, part or no parameters set. Any missing parameter values
are collected via interactive method.

By default, the script runs "live" -- creating the required database, login and user on a localhost
SQL Server instance. The SQL Server target can be overridden on the commandline.

In addition, running with the <code>--generate</code> commandline switch will dump the script
instead of running it live so that it can be used later, at a more convenient time.