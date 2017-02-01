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
