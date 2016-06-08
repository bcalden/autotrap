#!/usr/bin/python

__author__ = 'brian alden'
__email__ = 'brianalden@gwmail.gwu.edu'


import os, subprocess, re, pyrap.tables as pt, sys
from optparse import OptionParser
from datetime import datetime

uv_min_max = {'0': {'uvmin': 250, 'uvmax': 7500},
              '1': {'uvmin': 240, 'uvmax': 7200},
              '2': {'uvmin': 233, 'uvmax': 6977},
              '3': {'uvmin': 222, 'uvmax': 6667},
              '4': {'uvmin': 210, 'uvmax': 6294},
              '5': {'uvmin': 204, 'uvmax': 6122},
              '6': {'uvmin': 199, 'uvmax': 5960},
              '7': {'uvmin': 191, 'uvmax': 5732}}

class Parameters:
    def __init__(self, params):
        self.operation = params['operation']
        self.numthreads = params['numthreads']
        self.image = params['image']
        self.ms = params['ms']
        self.uvrange = params['uvrange']
        self.wmax = params['wmax']
        self.npix = params['npix']
        self.cellsize = params['cellsize']
        self.oversample = params['oversample']
        self.weight = params['weight']
        self.robust = params['robust']
        self.niter = params['niter']
        self.select = params['select']

    def write_params(self, param_file_name):
        """
        write_params(param_file_name) -> None

        writes the .params file to the passed filename
        """
        params = vars(self)
        strings = ["%s=%s" % (k, v) for k, v in params.iteritems()]
        with open(param_file_name, 'w') as f:
            f.write('\n'.join(strings))


def print_log(log):
    time = str(datetime.now())
    sys.stdout.write("*" * 25 + "\n")
    sys.stdout.write("%s\t" % time)
    sys.stdout.write("%s" % log + '\n')
    sys.stdout.write("*" * 25 + '\n')
    sys.stdout.flush()


def get_field_list(path, from_files=False):
    if not from_files:
        dir_list = os.listdir(path)
        fields = [name for name in dir_list if name.startswith("H")]
    else:
        dir_list = os.listdir(path)
        fields = [name[:7] for name in dir_list if name.endswith("restored.corr")]
        fields = list(set(fields))
    return fields


def get_options():
    parser = OptionParser()
    parser.add_option("-n", "--num_slices", dest="num_slices", help="Number of images to slice MS dataset into",
                      default=1, type="int")
    parser.add_option("-t", "--time_slice", dest="time_slice", help="Time of each slice in seconds", default="0") # not implemented yet
    parser.add_option("-m", "--ms_directory", dest="ms_file_directory", help="Directory containing the MS files",
                      default="")
    parser.add_option("-o", "--output_directory", dest="output_directory", help="Directory to output images to.",
                      default="")
    parser.add_option("-p", "--input_parameters", dest="input_parameters",
                      help="Allows the user to enter the parameter file parameters one by one", action="store_true",
                      default=False)
    parser.add_option("-d", "--param_directory", dest="param_directory",
                      help="The directory to output the parameter files to.", default="")
    parser.add_option("-i", "--iterations", dest="iterations", help="Number of cleaning iterations", default="2500")
    parser.add_option("-r", "--rejected_images", dest="db_with_rejections",
                      help="Make fits images for rejected images within the supplied database", default="")
    parser.add_option("-f", "--fits_from_field", dest="fits_from_field",
                      help="Make fits images for a field", action="store_true", default=False)
    parser.add_option("-s", "--no_overwrite", dest="no_overwrite", action="store_true", default=False)

    (options, args) = parser.parse_args()
    return options


def get_file_directory(prompt_string):
    """ get_file_directory() -> str

    Get the directory containing all of the .MS files.
    Can also supply a directory containing field directories which themselves contain the .MS files
    """

    directory = raw_input("Enter full path of directory containing %s: " % prompt_string)
    while directory is "":
        print "You did not enter a path!"
        directory = raw_input("Enter full path of directory containing %s: ")

    return directory


def get_output_directory():
    """ get_output_directory() -> str

    Gets the output directory supplied by the user.
    Try to create the directory and raise an error only if unable to create the directory for a reason other than
    it already existing.

    See:
    http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary/14364249#14364249
    """
    directory = raw_input("Enter full path for directory to output images to: ")
    try:
        os.makedirs(directory)
    except OSError:  # This code does not stop program execution if the directory exists. Only if it cannot create it.
        if not os.path.isdir(directory):
            raise
    return directory


def get_param_directory():
    """ get_param_directory() -> str

    Gets the directory to store the parameter files supplied by the user.
    Try to create the directory and raise an error only if unable to create the directory for a reason other than
    it already existing.

    See:
    http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary/14364249#14364249
    """
    directory = raw_input("Enter full path for directory to output the parameter files to: ")
    try:
        os.makedirs(directory)

    except OSError:  # This code does not stop program execution if the directory exists. Only if it cannot create it.
        if not os.path.isdir(directory):
            raise
    return directory


def get_empty_options(options):
    """ get_empty_options(options) -> returns options

    This function only gets the options which no default is supplied.
    That is, the directory containing the MS files and the directory for image and parameter file output.
    """
    if options.ms_file_directory == "":
        options.ms_file_directory = get_file_directory("MS files or fields")
    if options.output_directory == "":
        options.output_directory = get_output_directory()
    if options.param_directory == "":
        options.param_directory = get_param_directory()

    return options


def get_input_parameters(options):
    """ get_input_parameters -> dict

    Prompts the user to input the values for the .params file if user passed the right argument.
    Otherwise, return the default parameters.
    The only exceptions to this are the image and the ms values which will be algorithmically supplied
    """
    if options.input_parameters:
        params = {"operation": raw_input("Enter the operation (csclean [default], image, multiscale, predict, empty): ") or "csclean",
                  "numthreads": raw_input("Enter the number of threads (default: 1): ") or "1",
                  "image": None,  # user not entering this parameter, it is supplied by the software
                  "ms": None,  # user not entering this parameter, it is supplied by the software
                  "uvrange": raw_input("Enter the uv range (default: 0.1~3klambda): ") or "0.1~3klambda",
                  "wmax": raw_input("Enter the wmax (default: 5000): ") or "5000",
                  "npix": raw_input("Enter the number of pixels (default: 2048): ") or "2048",
                  "cellsize": raw_input("Enter the cell size (default: 30arcsec): ") or "30arcsec",
                  "oversample": raw_input("Enter the oversample (default: 5): ") or "5",
                  "weight": raw_input(
                      "Enter the weight scheme (uniform, superuniform, natural, robust [default], briggsabs, radial") or "robust",
                  "robust": raw_input("Enter the robust weighting parameter (default 0.0): ") or "0.0",
                  "niter": raw_input("Enter the number of cleaning iterations (default: 2500)") or "2500",
                  "select": raw_input("Enter a TaQL selection string (default: empty): ") or ""}
    else:
        params = {"operation": "csclean",
                  "numthreads": "1",
                  "image": None,
                  "ms": None,
                  "uvrange": "0.1~3klambda",
                  "wmax": "5000",
                  "npix": "2048",
                  "cellsize": "30arcsec",
                  "oversample": "5",
                  "weight": "robust",
                  "robust": "0.0",
                  "niter": options.iterations,
                  "select": ""}

    return params


def get_band_from_file_name(ms_file):
    """get_band_from_file_name(ms_file) -> str

    Given a filename such as /scratch/balden/MS3_MVF/H226+75/L125487_SAP004_BAND7.MS
    search for BAND in the string and return the number after it
    """
    index = ms_file.find("BAND")
    band = ms_file[index+4] if ms_file[index+4] != "_" else ms_file[index+5]

    return band


def get_field_from_file_name(ms_file):
    """get_field_from_file_name(ms_file): -> str

    Given a filename such as /scratch/balden/MS3_MVF/H226+75/L125487_SAP004_BAND7.MS
    preform a regex search for H###+## and return that value in string format.
    """
    field = re.search(r'H\d{3}\+\d{2}', ms_file).group(0)
    return field


def get_ms_list(path):
    """ get_ms_files(path) -> list

    Given a path return a list containing all MS files.
    Each MS file in the list is represented as a dictionary structured as follows:
     MS FILE -> PATH: path to the file,
                FILENAME: file name,
                FIELD: field ,
                BAND: band,
                TIME: time,
                OBS: 0 (will be filled later with a 1 or 2)

    Return a list containing a dictionary for each MS file
    """
    dir_list = os.listdir(path)
    data = [name for name in dir_list if name.endswith('.MS')]
    ms_files = []
    for ms_file in data:
        path_to_file = "%s/%s" % (path, ms_file)
        band = get_band_from_file_name(path_to_file)
        field = get_field_from_file_name(path_to_file)
        time = get_time_for_file_name(path_to_file)
        ms_dict = {"PATH": path_to_file.replace("//", "/"), "FIELD": field, "BAND": band, "TIME": time, "OBS": 0}
        ms_files += [ms_dict]

    return ms_files


def get_ms_files(path):
    """ get_ms_files(path) -> list

    Return a list of all MS files. Main work is done by get_ms_list(path).
    If directory passed contains field sub-directories, call for each field sub-directory
    """
    ms_files = get_ms_list(path)
    if ms_files == []:
        fields = get_field_list(path)
        for field in fields:
            ms_files += get_ms_list("%s/%s" % (path, field))
    return ms_files


def get_time_for_file_name(ms_file):
    """get_time_for_file_name(ms_file) -> str

    Given an MS file, query it to get the time and then process the string to generate a time for a filename
    """
    time = pt.taql('calc ctod(mjdtodate([select TIME from %s LIMIT 1]))' % ms_file)
    # above returns something that looks like:
    #               {'array': ['2013/02/15/06:53:06.003'], 'shape': [1, 1]}
    # code below returns something that looks like (HH_MM_SS), e.g.:
    #               06_53_06
    file_name_time = time['array'][0].split('/')[-1].split(".")[0].replace(':', '_')
    return file_name_time


def get_timing_values(ms_file, slices):
    taql_file = pt.table(ms_file)
    start_time = taql_file[0]['TIME']
    end_time = taql_file[taql_file.nrows() - 1]['TIME']
    offset = (end_time-start_time)/float(slices)

    print_log("Slicing the image with:\nStart Time:\t%s\nEnd Time:\t%s\nOffset:\t%s" % (start_time, end_time, offset))
    taql_file.close()
    return start_time, end_time, offset


def does_file_exist(filename):
    print_log("Checking to see if file: %s exists." % filename)
    exists = os.path.exists(filename)
    output_str = "does" if exists else "does not"
    print_log("%s %s exist." % (filename, output_str))
    return exists


def make_images(ms_files, options, params):
    check_each_file = True
    overwrite = False

    if options.no_overwrite:
        check_each_file = False
        overwrite = False

    for ms_file in ms_files:
        print_log("Starting on MS file: %s" % ms_file['PATH'])

        slicing_the_image = options.num_slices > 1
        if slicing_the_image:
            start_time, end_time, offset = get_timing_values(ms_file['PATH'], options.num_slices)
        for i in range(options.num_slices):

            if slicing_the_image:
                image_name = "%s_%s_BAND%s_n%s_SLICE%d.img" % (ms_file['FIELD'], ms_file['TIME'], ms_file['BAND'], params['niter'], i)
            else:
                image_name = "%s_%s_BAND%s_n%s.img" % (ms_file['FIELD'], ms_file['TIME'], ms_file['BAND'], params['niter'])

            if does_file_exist("%s/%s.restored.corr" % (options.output_directory, image_name)) and check_each_file:
                users_choice = None
                while not users_choice:
                    users_choice = raw_input("%s already exists.\nWould you like to overwrite it? (Y)es, (N)o, Yes to All (YA), No to All (NA): " % image_name)
                if users_choice.lower() is "y":
                    overwrite = True
                elif users_choice.lower() is "n":
                    overwrite = False
                elif users_choice.lower() is "ya":
                    overwrite = True
                    check_each_file = False
                elif users_choice.lower() is "na":
                    check_each_file = False
                    overwrite = False

            if not does_file_exist("%s/%s.restored.corr" % (options.output_directory, image_name)) or overwrite:
                params['image'] = str("%s/%s" % (options.output_directory, image_name)).replace("//", "/")
                params['ms'] = ms_file['PATH']

                if slicing_the_image:
                    params['select'] = 'TIME > ' + str(start_time + (i * offset)) + ' && TIME < ' + str(start_time + ((i + 1) * offset))

                print_log("Creating parameter file.")
                param_file = Parameters(params)
                param_file_name = ("%s/%s.params" % (options.param_directory, image_name)).replace("//", "/")
                param_file.write_params(param_file_name)

                print_log("Created parameter file: %s" % param_file_name)

                print_log("Staring awimager on %s" % param_file_name)
                subprocess.call(["awimager", param_file_name])
                print_log("Finished awimager on %s" % param_file_name)

                print_log("Generating addImagingInfo string for %s" % image_name)

                arguments_for_imaging_info = "%(restored_corr)s.restored.corr \"\" %(uvmin)d %(uvmax)d %(ms_file)s" \
                                             % {'restored_corr': params['image'],
                                                'uvmin': uv_min_max[ms_file['BAND']]['uvmin'],
                                                'uvmax': uv_min_max[ms_file['BAND']]['uvmax'],
                                                'ms_file': params['ms']}
                print_log("Starting addImagingInfo %s" % arguments_for_imaging_info)
                subprocess.call("addImagingInfo %s" % arguments_for_imaging_info, shell=True)
                print_log("Finished addImagingInfo on %s" % image_name)
            else:
                print_log("Skipping %s" % image_name)


def get_field_from_user(fields):
    num_fields = len(fields)
    index = range(num_fields)

    indexed_field_list = zip(index, fields)
    indexed_field_list = ["%d: %s" % z for z in indexed_field_list]
    print "Select which field to print: "
    print "\n".join(indexed_field_list)
    selected_field = input("Select field from above list (enter field index number): ")

    return fields[selected_field]


def get_restored_corr_files(directory, field):
    corr_list = os.listdir(directory)

    list_of_res_corr_files = [name for name in corr_list if name.endswith("restored.corr") and name.startswith(field)]

    return list_of_res_corr_files

def make_fits(input_file, output_file):
    string_to_run = "image2fits in=%s out=%s" % (input_file, output_file)
    print_log("Running: %s" % string_to_run)
    subprocess.call(string_to_run, shell=True)


def make_fits_from_field(options):
    restored_corr_directory = get_file_directory(".restored.corr files to make fits images from")
    fields = get_field_list(restored_corr_directory, from_files=True)
    selected_field = get_field_from_user(fields)
    res_corr_files = get_restored_corr_files(restored_corr_directory, selected_field)
    for res_corr_file in res_corr_files:
        input_image = "%s/%s" % (restored_corr_directory, res_corr_file)
        if options.output_directory is not "":
            output_image = "%s/%s.fits" % (options.output_directory, res_corr_file)
        else:
            output_image = "%s.fits" % input_image
        make_fits(input_image, output_image)


if __name__ == "__main__":
    options = get_options()
    if options.db_with_rejections is not "":
        None
    elif options.fits_from_field:
        print_log("Make fits from field")
        make_fits_from_field(options)
    else:
        options = get_empty_options(options)
        if options.input_parameters:
            get_input_parameters()

        params = get_input_parameters(options)
        print_log("Building dictionary of MS files")
        ms_files = get_ms_files(options.ms_file_directory)
        print_log("Beginning to make images")
        make_images(ms_files, options, params)
