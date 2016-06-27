autotrap
==========
Table of Contents
-----------
* [Project Overview](#project-overview)
* [Getting Started](#getting-started)
* [image_automator.py](#image_automatorpy)
* [generate_trap.py](#generate_trappy)
* [templates.py](#templatespy)
* [graph_tools.py](#graph_toolspy)
* [Contributing](#contributing)

#Project Overview
Autotrap is a collection of automation utilities for use with the LOFAR Transient Pipeline (TraP - https://github.com/transientskp/tkp) and AWImager.
There are three main files used for image generation, sending the images to the TraP, and generating graphs as output. These files are image_automator.py, generate_trap.py, and graph_tools.py respectively.
The other file included, templates.py is called by generate_trap.py and contains templates for TraP parameters.
Descriptions of each with examples can be found below. For further usage information, please see the wiki - https://github.com/bcalden/autotrap/wiki.

#Getting Started



# image_automator.py

##Usage
This is designed to be run from the commandline and supplied with some of the options described below. It can be imported and the functions used individually, but ideally, it is run by itself.
Before running image_automator.py, it is highly recommended to change the default parameters used in the parameter file creation. This can also be done at runtime by running with the -p option.
If you would rather change the defaults in the actual code, they are contained in the `get_input_parameters(options)` function within a dictionary named `params`.

Usage: image_automator.py [options]

## Options

|   Option              | Long option                           | Description                                                       |
|-----------------------|---------------------------------------|-------------------------------------------------------------------|
|  -h                   | --help                                | Show the usage instruction and available options (this table)     |
|  -n number            |  --num_slices=NUM_SLICES              | Number of images to slice MS dataset into                         |
|  -m directory         |  --ms_directory=MS_FILE_DIRECTORY     | Directory containing the MS files                                 |
|  -o directory         |  --output_directory=OUTPUT_DIRECTORY  | Directory to output images to.                                    |
|  -p                   |  --input_parameters                   | Allows the user to enter the parameter file parameters one by one |
|  -d directory         |  --param_directory=PARAM_DIRECTORY    | The directory to output the parameter files to.                   |
|  -i number            |  --iterations=ITERATIONS              | Number of cleaning iterations                                     |
|  -r database          |  --rejected_images=DB_WITH_REJECTIONS | Make fits images for rejected images within the supplied database |
|  -f                   |  --fits_from_field                    | Make fits images for a field                                      |
|  -s                   |  --no_overwrite                       | Don't overwrite any of the images                                 |

Example: `python image_automator.py -n 7 -m /scratch/balden/MS3_MVF -o /scratch/balden/timeslice/images -d /scratch/balden/timeslice/params -s &`
This example would take .MS files from the `/scratch/balden/MS3_MVF` directory, generate the parameter files and save them to `/scratch/balden/timeslice/params`. From there it will run AWImager on the parameter files as they are generated and store the resulting `.restored.corr` files in `/scratch/balden/timeslice/images`. It should be noted that as the `-n 7` option was passed, each .MS file will result in 7 `.restored.corr` files. Further, as the `-s` option was passed, if the files already exist they will not be overwritten. This option is useful when you are restarting a previously stopped run of the automator.


## MS Directory
When running image_automator, you must pass it the directory containing all of the .MS files. There are two directory structures image_automator supports.
They are as follows:

### Sub Directories
-Each field has its own folder full of .MS files
```
/scratch/userfolder
│   random_files.txt
│   random_script.py
│
└───MSSS_DATA
    ├───H218+68
    │   │   BAND0_OBS1.MS
    │   │   BAND0_OBS2.MS
    │   │   BAND1_OBS1.MS
    │   │   BAND1_OBS2.MS
    │   │   ...
    │   │   BAND7_OBS1.MS
    │   │   BAND7_OBS2.MS
    │
    └───H229+70
    │   │   BAND0_OBS1.MS
    │   │   BAND0_OBS2.MS
    │   │   BAND1_OBS1.MS
    │   │   BAND1_OBS2.MS
    │   │   ...
    │   │   BAND7_OBS1.MS
    │   │   BAND7_OBS2.MS
    ...
```

### One Big Directory
```
/scratch/userfolder
│   random_files.txt
│   random_script.py
│
└───MSSS_DATA
    │   H218+68_BAND0_OBS1.MS
    │   H218+68_BAND0_OBS2.MS
    │   H218+68_BAND1_OBS1.MS
    │   H218+68_BAND1_OBS2.MS
    │   ...
    │   H218+68_BAND7_OBS1.MS
    │   H218+68_BAND7_OBS2.MS
    │   H229+70_BAND0_OBS1.MS
    │   ...
    │   H229+70_BAND7_OBS1.MS
    │   H229+70_BAND7_OBS2.MS
    ...
```



### Parameters passed to addImagingInfo

|   Band    |   uv min  |   uv max  |
|-----------|-----------|-----------|
|   0       |   250     |   7500    |
|   1       |   240     |   7200    |
|   2       |   233     |   6977    |
|   3       |   222     |   6667    |
|   4       |   210     |   6294    |
|   5       |   204     |   6122    |
|   6       |   199     |   5960    |
|   7       |   191     |   5732    |

## `make_images(ms_files, options, params)`
This is the main function in image_automator. This function takes a dictionary of .MS files
(created by the `get_ms_files` function), options passed from the command line or the `get_options` function, and
 a parameter dictionary as generated by the `get_input_parameters` function.

This function iterates through a dictionary of MS files, generates their parameter files for use with AWImager, runs AWImager on that parameter file, and then runs addImagingInfo on the generated .restored.corr file.



#generate_trap.py

##Overview
This script essentially creates the configuration files required for TraP to run, and then runs TraP.

##Dependencies
* templates.py *(included in this repository)*
##Usage

#templates.py
##Overview
The templates.py file contains the templates for pipeline.cfg, job_config.cfg, and images_to_process used by the transient pipeline (TraP) and generate_trap.py. Each of these templates are stored in multiline strings and require customization to your particular user attributes before first use. It is HIGHLY recommended that if generate_trap.py is used, the templates.py file is not accessible by anyone you would not want to have access to your username and password. These two attributes are input in the `pipeline` string.
##Usage

#graph_tools.py

The graph_tools.py script contains multiple functions for different types of graph generation. This includes graphing the RMS noise, the variability parameters (V vs. Eta), etc.

##Dependencies
* [MatPlotLib 1.5.1](#http://matplotlib.org)
* [psycopg2](#http://initd.org/psycopg/)

#Contributing