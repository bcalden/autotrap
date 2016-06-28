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
Autotrap is a collection of automation utilities for use with the [LOFAR Transient Pipeline (TraP)](https://github.com/transientskp/tkp) and AWImager.
With these tools, one can automate image creation, simplify configuring and running the TraP on these images, and generating graphs helpful for data analysis.
There are three main files used for image generation, sending the images to the TraP, and generating graphs as output. These files are [image_automator.py](#image_automatorpy), [generate_trap.py](#generate_trappy), and [graph_tools.py](#graph_toolspy) respectively.
The other file included, [templates.py](#templatespy) is called by generate_trap.py and contains templates for TraP parameters.
Descriptions of each with examples can be found below.

#Installing / Getting Started
## Installing
To install this project, simply run `git clone https://github.com/bcalden/autotrap.git` in your command line. This command should download this repository to whatever your current directory is and place it in the newly created `autotrap` directory. Nothing further needs to be installed (unless you need any of the dependencies).

## Dependencies
* [Transient Pipeline (TraP)](https://github.com/transientskp/tkp)
* [MatPlotLib 1.5.1](http://matplotlib.org)
* [psycopg2](http://initd.org/psycopg/)
* [pexpect](https://pexpect.readthedocs.io/en/stable/)

## Sample Work Flow
Say you have a set of data in .MS format that you want convert to images, put into TraP, and analyze the results. This workflow is for you!
 Note: for a full list of options each step of the way, please read the section pertaining to the respective part.

###Make the Images
The first step of the process is to convert the .MS files into images. This can be achieved by running the [image automator](#image_automator.py) on the data.
Lets say all of the .MS files were located in the folder `/scratch/username/ms_data/MS3_dataset/`.
In this example, you aren't going to slice the images up into smaller files (but there is an example below which covers that).
The automator will generate the parameter files and the images so you have to provide directories where it should write to.
Lets say you want the .param files stored in `/scratch/username/ms_data/MS3_params/` and the images stored in `/scratch/username/ms_data/MS3_Images/`.
You would then run the following command to start the image automator.

`nohup python /[path_to_the_autotrap]/autotrap/image_automator.py -m /scratch/username/ms_data/MS3_dataset/ -d /scratch/username/ms_data/MS3_params/ -o /scratch/username/ms_data/MS3_Images/ > ms3_image_output.log &amp; `

The `nohup` command and the `&amp;` may be confusing if you are not familiar with them.
#### nohup
Running the nohup command ensures whatever command you place after it (in this case, the image automator) continues even after you exit the terminal session. The `> ms3_image_output.log` at the end of the command forwards all output to the file `ms3_image_output.log` instead of the terminal. Further information can be found [here](http://linux.die.net/man/1/nohup).

#### &amp;
The `&amp;` at the end of the command places the task in the background. This allows you access to the commandline to either run other tasks or monitor the output while still using the `nohup` command.

*Note: To monitor the output of the automator while running it in the background, you can run `tail -f ms3_image_output.log`.*

###Put the Images Into TraP
You now have a set of newly created images (in .restored.corr format) located in `/scratch/username/ms_data/MS3_Images/`. To get these into TraP, you can run [generate_trap.py](#generate_trappy). *Be sure to put your username / password in the [templates.py](#templatespy) file.*

`nohup python /[path_to_autotrap]/autotrap/generate_trap.py --name bca_ms3_images --images /scratch/username/ms_data/MS3_Images --elliptical 2.0 > trap_output.log &amp;`

Running the above command would create the configuration files and run TraP. The database name would be bca_ms3_images.

###Generate Graphs
Now that the data is in Banana, you can begin to analyze the data and generate graphs. A common graph is the η<sub>ν</sub> vs. V<sub>ν</sub> graph. To create this, follow the instructions in the section on[graph_tools.py](#graph_toolspy).

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

Example:
`python image_automator.py -n 7 -m /scratch/balden/MS3_MVF -o /scratch/balden/timeslice/images -d /scratch/balden/timeslice/params -s &`

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
This script creates the configuration files required for TraP to run, and then runs TraP. It creates the configuration files based upon the strings in `templates.py`. Prior to running it is imperative that you go through the `templates.py` file and change the parameters as indicated in [the templates.py section](#templatespy)

##Dependencies
* [Transient Pipeline (TraP)](https://github.com/transientskp/tkp)
* templates.py *(included in this repository)*

##Usage
Usage: generator.py [options]

##Options:
|   Option                  | Long option                   | Description                                                       |
|---------------------------|-------------------------------|--------------------------------------------------|
|  -h                       |   --help                      |   show this help message and exit
|  -n DATABASE              |   --name=database_name        |   database name
|  -b HIGH_BOUND            |   --high-bound=#              |   multiplied with noise to define upper threshold
|  -e ELLIPTICAL            |   --elliptical=#              |   threshold for elliptical check
|  -f FORCE_BEAM            |   --force_beam=true/false     |   Toggle force beam (true or false)
|  -d DETECTION_THRESHOLD   |   --detection_threshold=#     |   Set the detection threshold
|  -i IMAGES                |   --images=directory          |   folder containing images to process
|  -x EXT                   |   --extension=file_extension  |   extension of files in images folder *(defaults to .restored.corr)*
|  -s SETUP                 |   --setup=database_name       |   Setup initial options
|  -r DROPDBNAME            |   --dropdb=database_name      |   deletes the database *(provided it is one you can delete)*

Example: python generate_trap.py --name balden_sliced_high_250_ellip_5 --images /scratch/balden/Images/sliced --elliptical 5.0 --high-bound 250 &


#templates.py

##Overview
The templates.py file contains the templates for pipeline.cfg, job_config.cfg, and images_to_process used by the transient pipeline (TraP) and generate_trap.py.
Each of these templates are stored in multiline strings and require customization to your particular user attributes before first use. It is HIGHLY recommended that if generate_trap.py is used, the templates.py file is not accessible by anyone you would not want to have access to your username and password. These two attributes are input in the `pipeline` string.

##Usage
Prior to running `generate_trap.py` you need to edit the template strings so they contain your particular user information.
As this script is all about ease of use, it follows some rather lax security practices such as storing database usernames and passwords.
Because of this, `autotrap` and `templates.py` in specific should only be installed in a directory that only you or people you are ok with having your database password have access to.

The file is three strings for generation of pipeline.cfg, job_config.cfg, and images_to_process. In the pipeline string, your username and password for the PostgreSQL database should be entered between the quotes. If any of the server is not correct, it can be updated as well.
Nothing needs to be updated in images_to_process. The job_config string can be updated with default values for each setting.

#graph_tools.py

##Overview
The graph_tools.py script contains multiple functions for different types of graph generation. This includes graphing the RMS noise, the variability parameters (V vs. Eta), etc.

##Dependencies
* [MatPlotLib 1.5.1](http://matplotlib.org)
* [psycopg2](http://initd.org/psycopg/)

##Usage
At the top of the file you should add your database username, password, and the database name you want to generate the graphs for. As this is a not the best security practice, it is strongly advised that autotrap should be stored in a directory that can only be accessed by you or people you don't mind having your database username or password. This will be updated in the next revision.
To use this script, you can either import the file into the Python REPL, or into a iPython/Jupyter notebook. It can also be run directly by editing the `__main__` portion of the file to include the graphs you want generated.


### η<sub>ν</sub> vs. V<sub>ν</sub>
`create_graph_v_vs_eta(data, outputname, inc_simulated=False)`

This function queries the database name indicated at the top of the file to get the η<sub>ν</sub> and V<sub>ν</sub> values for each source. Simulated data can be included by providing the text files listed within the function. These simulated files were obtained from [Antonia Rowlinson's](https://github.com/AntoniaR) [TraP_Trans_Tools](https://github.com/AntoniaR/TraP_trans_tools). The graph is saved in your current directory and is named whatever was supplied as the output name.



##Future Development
Update to accept command line arguments for username, password, database name, and type of graphs. Change `__main__` functionality to either use options passed at the command line or query the user for the options. Further areas of development potential are seeing how this can be integrated with TraP's usage of SQLAlchemy.

#Contributing
Contributions are greatly appreciated. If you have a bug request or think there is a better way to implement some part of this project, feel free to fill out an issue on GitHub.