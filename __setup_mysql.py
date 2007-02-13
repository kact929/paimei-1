#!c:\python\python.exe

import MySQLdb
import sys

USAGE = "__setup_mysql.py <mysql host> <username> <password>"
error = lambda msg: sys.stderr.write("ERROR> " + msg + "\n") or sys.exit(1)

if len(sys.argv) != 4:
    error(USAGE)

host     = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]

try:
    mysql = MySQLdb.connect(host=host, user=username, passwd=password)
except MySQLdb.OperationalError, err:
    error("Failed connecting to MySQL server: %s" % err[1])

cursor = mysql.cursor()

try:
    cursor.execute("CREATE DATABASE paimei")
    cursor.execute("USE paimei")

    cursor.execute("""CREATE TABLE cc_hits (
      target_id int(10) unsigned NOT NULL default '0',
      tag_id int(10) unsigned NOT NULL default '0',
      num int(10) unsigned NOT NULL default '0',
      timestamp int(10) unsigned NOT NULL default '0',
      eip int(10) unsigned NOT NULL default '0',
      tid int(10) unsigned NOT NULL default '0',
      eax int(10) unsigned NOT NULL default '0',
      ebx int(10) unsigned NOT NULL default '0',
      ecx int(10) unsigned NOT NULL default '0',
      edx int(10) unsigned NOT NULL default '0',
      edi int(10) unsigned NOT NULL default '0',
      esi int(10) unsigned NOT NULL default '0',
      ebp int(10) unsigned NOT NULL default '0',
      esp int(10) unsigned NOT NULL default '0',
      esp_4 int(10) unsigned NOT NULL default '0',
      esp_8 int(10) unsigned NOT NULL default '0',
      esp_c int(10) unsigned NOT NULL default '0',
      esp_10 int(10) unsigned NOT NULL default '0',
      eax_deref text NOT NULL default '',
      ebx_deref text NOT NULL default '',
      ecx_deref text NOT NULL default '',
      edx_deref text NOT NULL default '',
      edi_deref text NOT NULL default '',
      esi_deref text NOT NULL default '',
      ebp_deref text NOT NULL default '',
      esp_deref text NOT NULL default '',
      esp_4_deref text NOT NULL default '',
      esp_8_deref text NOT NULL default '',
      esp_c_deref text NOT NULL default '',
      esp_10_deref text NOT NULL default '',
      is_function int(1) unsigned NOT NULL default '0',
      module varchar(255) NOT NULL default '',
      base int(10) unsigned NOT NULL default '0',
      PRIMARY KEY  (target_id,tag_id,num),
      KEY tag_id (tag_id),
      KEY target_id (target_id)
    ) TYPE=MyISAM""")

    cursor.execute("""CREATE TABLE cc_tags (
      id int(10) unsigned NOT NULL auto_increment,
      target_id int(10) unsigned NOT NULL default '0',
      tag varchar(255) NOT NULL default '',
      notes text NOT NULL default '',
      PRIMARY KEY  (id)
    ) TYPE=MyISAM""")

    cursor.execute("""CREATE TABLE cc_targets (
      id int(10) unsigned NOT NULL auto_increment,
      target varchar(255) NOT NULL default '',
      notes text NOT NULL default '',
      PRIMARY KEY  (id)
    ) TYPE=MyISAM""")
except MySQLdb.ProgrammingError, err:
    error("Failed creating db / tables: %s" % err[1])

cursor.close()