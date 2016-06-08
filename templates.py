pipeline = """[DEFAULT]
runtime_directory = %(cwd)s
job_directory = %(runtime_directory)s/%(job_name)s

[logging]
#log_dir contains output log, plus a copy of the config files used.
log_dir = %(job_directory)s/logs/%(start_time)s
debug = False
colorlog = True

[database]
engine = postgresql ;(monetdb or postgresql)
database = "%(database)s" ;
user =  "" ; <----- PUT USERNAME IN QUOTES
password = "" ; <----- PUT PASSWORD IN QUOTES
host = "vlo.science.uva.nl"
port =
passphrase =
dump_backup_copy = False

[image_cache]
copy_images = True
mongo_host = "localhost"
mongo_port = 27017
mongo_db = "tkp"


[parallelise]
method = "multiproc"  ; or serial
cores = 0  ; the number of cores to use. Set to 0 for autodetect"""

images_to_process = """###################################################################################
#      List the images for processing by the transient detection pipeline         #
###################################################################################

# This should provide a module-scope iterable named "images" which provides a
# full path to each image to be processed. For example:

#images = [
#    "/path/to/image1",
#    "/path/to/image2",
#]

# Optionally, whatever standard tools are required may be used to generate the
# list:
#
import os
import glob
images = sorted(glob.glob(os.path.expanduser("%(dir)s/*.%(ext)s")))

#Display the list of images to be processed whenever this file is imported:
# (can be used for quick checking via an ipython import)
print "******** IMAGES: ********"
for f in images:
    print f
print "*************************\""""

job_config = """[persistence]
description = "TRAP dataset"
dataset_id = -1
#Sigma value used for iterative clipping in RMS estimation:
rms_est_sigma = 4
#Determines size of image subsection used for RMS estimation:
rms_est_fraction = 8

[quality_lofar]
low_bound = 1           ; multiplied with noise to define lower threshold
high_bound = %(high_bound)s        ; multiplied with noise to define upper threshold (def 80)
oversampled_x = 30      ; threshold for oversampled check
elliptical_x = %(elliptical)s      ; threshold for elliptical check
min_separation = 10     ; minimum distance to a bright source (in degrees)

[source_extraction]
# extraction threshold (S/N)
detection_threshold = %(detection_threshold)s
analysis_threshold = 3
back_size_x = 50
back_size_y = 50
margin = 10
deblend_nthresh = 0 ; Number of subthresholds for deblending; 0 disables
extraction_radius_pix = 250
force_beam = %(force_beam)s
box_in_beampix = 10
# ew/ns_sys_err: Systematic errors on ra & decl (units in arcsec)
# See Dario Carbone's presentation at TKP Meeting 2012/12/04
ew_sys_err = 10
ns_sys_err = 10
expiration = 10  ; number of forced fits performed after a blind fit

[association]
deruiter_radius = 5.68
beamwidths_limit =  1.0

[transient_search]
new_source_sigma_margin = 3
"""
