import sys
import templates
import os
from optparse import OptionParser
import subprocess
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pexpect
import shutil


db_type = 'postgres'
host_address = 'vlo.science.uva.nl'
username = '' # put username here
pass = '' # put password here


def createdb(database):
    con = None
    con = connect(dbname=db_type, user=username, host=host_address, password=pass)

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute('CREATE DATABASE ' + database)
    cur.close()
    con.close()


def grant_access(database):
    con = None
    con = connect(dbname=db_type, user=username, host=host_address, password=pass)

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO banana;")
    cur.close()
    con.close()

def dropdb(database):
    print_log("Dropping the database: %s" % database)
    con = None
    con = connect(dbname=db_type, user=username, host=host_address, password=pass)

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute('DROP DATABASE ' + database)

    cur.close()
    con.close()
    print_log("Database dropped")

def db_already_exists(db_name):
    con = None
    try:
        con = connect(dbname=db_type, user=username, host=host_address, password=pass)
    except:
        print "Database doesn't exist"
        return False
    con.close()
    return True


def write_pipeline_cfg(database):
    contents = templates.pipeline % {'cwd': '%(cwd)s',
                                     'runtime_directory': '%(runtime_directory)s',
                                     'job_name': '%(job_name)s',
                                     'job_directory': '%(job_directory)s',
                                     'start_time': '%(start_time)s',
                                     'database': database
                                     }
    file = open("/scratch/balden/%s/pipeline.cfg" % database, 'w')

    file.write(contents)
    file.close()


def write_images_to_process(database, images, ext):
    contents = templates.images_to_process % {'dir': images,
                                              'ext': ext}

    file = open("/scratch/balden/%s/%sjob/images_to_process.py" % (database, database), 'w')
    file.write(contents)

    file.close()


def write_job_config(high_bound, elliptical, force_beam, detection_threshold, database):
    contents = templates.job_config % {'high_bound': high_bound,
                                       'elliptical': elliptical,
                                       'detection_threshold': detection_threshold,
                                       'force_beam': force_beam}

    file = open("/scratch/balden/%s/%sjob/job_params.cfg" % (database, database), 'w')

    file.write(contents)
    file.close()


def get_empty_options(options):
    if options.database is "":
        options.database = raw_input("Please enter a name for the database: ")
    if options.images is "":
        options.images = raw_input("Enter what folder to get the images directory name (located in /scratch/balden/Images/: ")


def del_dir(dir_name):
    print_log("Deleting directory /scratch/balden/%s" % dir_name)
    try:
        shutil.rmtree("/scratch/balden/"+dir_name)
    except:
        print_log("ERROR DELETING /scratch/balden/%s" % dir_name)
    print_log("Finished deleting /scratch/balden/%s" % dir_name)


def print_log(log):
    print "*"*25 + "\n%s" % log + '\n' + "*"*25


parser = OptionParser()
parser.add_option("-n", "--name", dest="database", help="database name", default="")
parser.add_option("-b", "--high-bound", dest="high_bound", help="multiplied with noise to define upper threshold", default=80)
parser.add_option("-e", "--elliptical", dest="elliptical", help="threshold for elliptical check", default=2.0)
parser.add_option("-f", "--force_beam", dest="force_beam", help="", default="True")
parser.add_option("-d", "--detection_threshold", dest="detection_threshold", help="", default=8)
parser.add_option("-i", "--images", dest="images", help="folder containing images to process", default="")
parser.add_option("-x", "--extension", dest="ext", help="extension of files in images folder", default="restored.corr")
parser.add_option("-s", "--setup", dest="setup", help="Setup initial options", default="False")
parser.add_option("-r", "--dropdb", dest="dropdbname", help="delete db", default="")
(options, args) = parser.parse_args()

# print "%s = %s" % ("name", options.database)
# print "%s = %s" % ("highbound", options.high_bound)
# print "%s = %s" % ("elliptical", options.elliptical)
# print "%s = %s" % ("force beam", options.force_beam)
# print "%s = %s" % ("detection threshold", options.detection_threshold)

if __name__ == "__main__":

    if not (options.dropdbname is ""):
        dropdb(options.dropdbname)
        del_dir(options.dropdbname)
        exit()

    get_empty_options(options)

    os.chdir("/scratch/balden/")
    write_db = True
    if db_already_exists(options.database):
        continue_with_db = raw_input("DB Already exists, continue with the same database (Y (default) / N): ")
        if not (continue_with_db is "" or continue_with_db is "Y" or continue_with_db is "y"):
            new_db_name = raw_input("Enter a new database name: ")
            options.database = new_db_name
        else:
            print("Using the same database")
            write_db = False

    subprocess.call(["trap-manage.py", "initproject", options.database])
    os.chdir("/scratch/balden/%s" % options.database)
    subprocess.call(["trap-manage.py", "initjob", "%sjob" % options.database])

    print_log("Writing config files")
    write_images_to_process(options.database, options.images, options.ext)
    write_pipeline_cfg(options.database)
    write_job_config(options.high_bound, options.elliptical, options.force_beam, options.detection_threshold, options.database)
    print_log("Finished writing config files")

    if write_db:
        print_log("Creating Database")
        createdb(options.database)
        print_log("Database Created")

        print_log("Running trap-manage.py initdb")
        child = pexpect.spawn('trap-manage.py initdb')
        child.logfile = sys.stdout  # pipe the output of trap-manage.py initdb to the screen (stdout)
        child.expect('.*Do you want to continue\? \[y/N\]:') # regex waiting for a string to pop up ending with Do you want...
        child.sendline('y') # yes you want to continue
        child.wait()  # wait for <trap-manage.py initdb> to complete before continuing
        print_log("Finished running trap-manage.py initdb")

        print_log("Granting access")
        grant_access(options.database)
        print_log("Finished granting access")

    print_log("Running trap-manage.py run %s" % options.database)
    subprocess.call(["trap-manage.py", "run", "%sjob" % options.database])
    print_log("Finished running trap-manage run %s" % options.database)
