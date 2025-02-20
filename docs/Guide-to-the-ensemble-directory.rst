.. _Guide to the Ensemble Directory:

The structure of the ensemble directory
==========

.. _Template:

The Template Run Directory
-------------

The CHEEREIO Template Run directory is essentially a standard GEOS-Chem run directory, generated by a routine within the ``setup_ensemble.sh`` script that is very much like the code that generates the standard GEOS-Chem run directory, though there are a few minor differences. This directory will then be copied by  ``setup_ensemble.sh`` to form the Spinup Run directory, the Control Run directory, and the individual ensemble members within the Ensemble Runs directory. Users should make sure that the Template Run directory meets all their requirements before any further copying takes place. 

Differences between the Template Run directory and a standard GEOS-Chem run directory are as follows. ``input.geos`` has empty tags for the start and end times, as this will allow CHEEREIO to resubmit GEOS-Chem runs for different time periods. ``HEMCO_Config.rc`` is represented by two template files. ``HEMCO_Config_SPINUP_NATURE_TEMPLATE.rc`` is for spinup and "nature" simulations, neither of which include randomized scaling factors (i.e. it is a normal HEMCO_Config.rc file generated by the usual run directory creation script). ``HEMCO_Config.rc`` is for ensemble members, all of whom will have perturbed emissions. References to gridded scaling factors are added at key lines in this config file. Finally, the template run directory has no batch script associated with it, as it cannot be run.

Although ``HEMCO_Config.rc`` is generated by the ``setup_ensemble.sh`` utility, it may not be automatically ready to use if you are distinguishing updates of different emissions sources of one species for a source attribution study (for example, updating NO agricultural emissions separately from the rest of NO emissions). For more information on how to handle this issue, see the :ref:`HEMCO verification` entry.

Users should pay attention to collections saved in ``HISTORY.rc`` and modify if desired. However, if using StateMet or LevelEdgeDiags collections during assimilation (e.g. for some TROPOMI assimilation runs), make sure to turn those on using the switches in ``ens_config.json`` rather than a direct modification of HISTORY.rc. This is because CHEEREIO modifies HISTORY.rc on the fly in some situations.

Aside from these subtleties, the user should modify the template run directory as freely as they would any GEOS-Chem run directory they are customizing for their own research.

.. _HEMCO verification:

Verifying HEMCO Config after initialization
~~~~~~~~~~~~~~

CHEEREIO uses the HEMCO module of GEOS-Chem to seamlessly pass emissions updates from the LETKF assimilation workflow to GEOS-Chem and back. HEMCO is able to accepted gridded emissions scaling factors from NetCDF files and apply them to input emissions inventories. Within the ``HEMCO_Config.rc`` file, gridded emissions scaling factors are linked to a given emissions inventory by a numerical tag. Below is an example where NO emissions from energy in the CEDS inventory is linked to gridded scale factors in the ``NOx_SCALEFACTOR.nc`` file by the tag 700; the second line is stored in the scaling factor section of the ``HEMCO_Config.rc`` file. 
::

   0 CEDS_NO_ENE     $ROOT/CEDS/v2021-06/$YYYY/NO-em-anthro_CMIP_CEDS_$YYYY.nc            NO_ene            1750-2019/1-12/1/0 C xy kg/m2/s NO    25/700        1 5
   ...
   700 ASSIM_NOx  /n/holyscratch01/jacob_lab/dpendergrass/GC-LETKF/NOx_4x5_v06/template_run/NOx_SCALEFACTOR.nc Scalar 2016-2016/1-12/1-31/0-23 RF xy 1  1

At initialization time, CHEEREIO passes through the ``HEMCO_Config.rc`` file, checks which inventories are turned on, and adds numerical tags to emissions of species that the user has indicated they will assimilate within the ``ens_config.json`` file. It then adds a line in the scaling factor section of the ``HEMCO_Config.rc`` file in order to link these emissions to a gridded scale factor file. During this check, CHEEREIO adds tags to any case where a species of interest is emitted; it does not distinguish between source types.

Some users may want to use CHEEREIO for source attribution studies (for example, updating NO agricultural emissions separately from the rest of NO emissions). To run this type of study, users can indicate that they would like to apply a separate set of gridded scaling factors to different source types for a given species from within the ``ens_config.json`` file. Below is a valid example which will separate update NO agricultural emissions separately from the rest of NO emissions:
::

   "CONTROL_VECTOR_EMIS" : {
      "NO_agriculture":"NO"
      "NO_other":"NO"
   },

However, the CHEEREIO install script is unable to recognize the difference between these source types, and instead will apply tags to any time when the emitted species (NO) appears. This is how the freshly installed ``HEMCO_Config.rc`` file will look for the same lines as shown above.
::

   0 CEDS_NO_ENE     $ROOT/CEDS/v2021-06/$YYYY/NO-em-anthro_CMIP_CEDS_$YYYY.nc            NO_ene            1750-2019/1-12/1/0 C xy kg/m2/s NO    25/700/701        1 5
   ...
   700 ASSIM_NO_agriculture  /n/holyscratch01/jacob_lab/dpendergrass/GC-LETKF/NOx_4x5_v06/template_run/NO_agriculture_SCALEFACTOR.nc Scalar 2016-2016/1-12/1-31/0-23 RF xy 1  1
   701 ASSIM_NO_other  /n/holyscratch01/jacob_lab/dpendergrass/GC-LETKF/NOx_4x5_v06/template_run/NO_other_SCALEFACTOR.nc Scalar 2016-2016/1-12/1-31/0-23 RF xy 1  1

The user will need to go through manually in this case and delete irrelevant tags. In the above example, the user would delete the 700 tag from the ``CEDS_NO_ENE`` entry.

Beyond the case of source attribution, the user should take additional care to make sure that the ``HEMCO_Config.rc`` file matches their intentions, especially if the user is extensively modifying inventories The user should pay special attention that scaling factors are not applied to inapplicable sources, such as negative emissions from soil uptake. See the  `GEOS-Chem Wiki Page for HEMCO_Config.rc <http://wiki.seas.harvard.edu/geos-chem/index.php/The_HEMCO_Config.rc_file>`__ for more information.

.. _spinup simulation:

The Spinup Run Directory
-------------

The Spinup Run directory, if it is enabled, functions like a normal GEOS-Chem run directory with input settings specified by ``ens_config.json``. The Spinup Run directory is a true run directory and comes with a run script that the user must execute manually; the run is initialized by the restart linked in the ``RESTART_FILE`` entry. The idea of this run is to produce a spun up restart that reflects realistic atmospheric conditions; this is "traditional" model spinup and is distinct from the "ensemble spinup" procedure, unique to ensemble data assimilation methods, which is discussed more extensively in the :ref:`Run Ensemble Spinup Simulations` section. 

The start and end times in ``input.geos`` are given by the ``SPINUP_START`` and ``SPINUP_END`` settings, while default cluster memory and wall time settings are specified by ``EnsCtrlSpinupMemory`` and ``SpinupWallTime`` respectively. See :ref:`Configuration` for more information. The Spinup Run Directory created is created by ``setup_ensemble.sh`` so long as the ``SetupSpinupRun`` switch is set to ``true`` when that script is run and so long as ``DO_SPINUP`` is switched to ``true`` in ``ens_config.json``.  

When the spinup run terminates, the end restart file generated will automatically be used to initialize the ensemble run directories. No copying on the user's part is necessary.

.. _control simulation:

The Control Run Directory
-------------

The control run is a normal GEOS-Chem simulation without any assimilation. The output of this simulation can be compared with the LETKF results in the postprocessing workflow, which provides useful indication of whether the LETKF has provided useful information. A control run will be created when the user sets ``DO_CONTROL_RUN`` to ``true`` in ``ens_config.json``. The postprocessing suite included with CHEEREIO automatically uses Control Run output to generate a variety of plots and data files that assess assimilation success.

Note that there are two ways to do a control simulation in CHEEREIO. 

* The preferred method, which is activated by setting ``DO_CONTROL_WITHIN_ENSEMBLE_RUNS`` to true in ``ens_config.json``, is to run the control simulation as an additional ensemble member with label 0 (ensemble members used for assimilation are numbered starting at 1). In this case, there will be no Control Run directory created at the top level of the ensemble directory (i.e. at the same level as the Template Run directory or the Ensemble Runs directory). The benefit of running the control simulation as an ensemble member is twofold: (1) No separate run script is required; the control run is executed at the same time the ensemble is run, and (2) the control simulation will be made to match non-assimilation adjustments performed on the ensemble, such as scaling concentrations to be non-biased relative to observations; this makes the control simulation directly comparable with the LETKF results. If this method is used, the control directory in this case is created automatically when the ``setup_ensemble.sh`` utility is used to create the ensemble. No special consideration is required by the user.
* If ``DO_CONTROL_WITHIN_ENSEMBLE_RUNS`` is set to false, and DO_CONTROL_RUN is set to true, then the control simulation is created as an additional run directory at the top directory level. This keeps the control simulation fully separate from the ensemble and any non-assimilation adjustments that are performed. In this case, you have to run the ``setup_ensemble.sh`` utility with the ``SetupControlRun`` switch set to ``true`` to create the control run directory. In this case, the Control Run directory is like the Spinup Run directory in that it functions like a normal GEOS-Chem run directory with input settings specified by ``ens_config.json``. Like the Spinup Run directory, the Control Run directory is a true run directory and comes with a run script (ending in ``.run``) that the user must execute manually via sbatch; the run is initialized by either the restart generated by the Spinup Run directory or by the restart linked in the ``RESTART_FILE`` entry of ``ens_config.json``, depending on whether the user is doing a spinup run within the CHEEREIO environment. **Note that the postprocessing workflow will fail if you indicate you are using a control run but that run hasn't completed at the time the postprocessing workflow is submitted.** In short, don't forget your control run! The start and end times in ``input.geos`` or ``geoschem_config.yml`` are given by the ``CONTROL_START`` and ``CONTROL_END`` settings, while default cluster memory and wall time settings are specified by ``EnsCtrlSpinupMemory`` and ``ControlWallTime`` respectively. See :ref:`Configuration` for more information. The Control Run Directory created is created by ``setup_ensemble.sh`` so long as the ``SetupControlRun`` switch is set to ``true`` when that script is run and so long as ``DO_CONTROL_RUN`` is switched to ``true`` and ``DO_CONTROL_WITHIN_ENSEMBLE_RUNS`` is set to ``false`` in ``ens_config.json``.  


The Scratch Directory
-------------

Although the user should **never modify anything in the scratch directory**, it may still be useful to know how CHEEREIO makes use of this folder throughout run time. There are three main types of file in the scratch directory:

* Column files (``.npy``): Column files contain assimilated columns which will eventually be combined and used to update ensemble restarts and scaling factors. Each core on each run instance calculates some number of columns at assimilation time and saves them to the scratch directory in a relevant subfolder, until finally all are computed and can be used to adjust the ensemble. 
* Internal state files: these files track things like the current date, lat/lon coordinates, and columns assigned to each core in the ensemble parallelization routine.
* Flag files: these files are used to couple the many jobs that are running simultaneously during a CHEEREIO assimilation routine. They track ensemble members as they finish GEOS-Chem, as columns are being saved, and as assimilation and clean up processes complete. If an ensemble member fails, it can generate a kill file that terminates the entire ensemble, saving computational resources. The reason these files are necessary is because GEOS-Chem is run as an array of jobs without any memory sharing or coordination, which allows for parallelization across many nodes without MPI. Coordination takes place by each job independently checking for these signal files and modifying their behavior accordingly. This procedure is discussed extensively in the :ref:`Run Ensemble Simulations` section.

The only reason to view the scratch directory is (1) to monitor run progress, and (2) debugging in the event of ensemble failure. In the latter case, the ``KILL_ENS`` file may contain a short error message that can help the user identify the most relevant log file for debugging. See the :ref:`Fix Kill Ens` section for more details on how to debug CHEEREIO and repair the ensemble for eventual resubmission.

.. _Ensemble Runs:

The Ensemble Runs Directory
-------------

The Ensemble Runs directory is created in two stages over the course of running ``setup_ensemble.sh``: ensemble run scripts are created when ``setup_ensemble.sh`` creates the Template Run directory, while the individual ensemble run directories are created when ``SetupEnsembleRuns`` is set to true after the Template Run directory has been created and (optionally) edited by the user. Contents of the completely created Ensemble Runs Directory are as follows:

* The ``run_ensemble_simulations.sh`` bash script is a complex batch submission script that manages the starting and stopping of a single GEOS-Chem ensemble member run, executes the subset of the LETKF operation that is assigned to this ensemble member (including coordinating internal core-wise parallelization), and, for the "master" ensemble member (always ensemble member 1), coordinates the overall ensemble (e.g. file clean-up, resynchronization, restart and scaling updates). More details are available in the :ref:`Run Ensemble Simulations` entry. **The user never executes this script directly.**
* The ``run_ens.sh`` bash script contains simple instructions on how to submit a job array of ensemble member simulations (i.e. instances of ``run_ensemble_simulations.sh``) to the SLURM scheduler. We recommend this script be executed via ``nohup bash run_ens.sh &``. After this command is given, the ensemble will run until completion.
* The ``log`` folder contains the vast number of log files produced by the ensemble as it runs. The only exception is GEOS-Chem log files, which are contained in the individual ensemble run directories. There are four types of files in the ``log`` folder:

   * ``ensemble_slurm_JOBNUMBER.err`` files. One such file is present for each ensemble member. These contain errors returned to the program on the shell-level. If all goes well, this will be empty. Otherwise, they can be very useful in determining what went wrong at runtime.
   * ``ensemble_slurm_JOBNUMBER.out`` files. One such file is present for each ensemble member. These contain regular output returned to the program on the shell-level. These won't have much in them and are rarely worth looking at.
   * ``letkf_ENSNUMBER_CORENUMBER.out`` files. One file is present for each core assigned columns to assimilate within each ensemble member. They contain real-time information about what this particular core is doing at assimilation time (including overall time taken to load files and compute assimilated columns). These files are useful for tracking run progress
   * The ``letkf_master.out`` file. Only one of these files is created by ensemble member 1, which is by default the "job manager" (coordinates ensemble members, does file clean-up and NetCDF updates, etc.). Like the other LETKF log files, this contains real-time information about the combination of assimilated columns and the updates of NetCDF files.

 * The ensemble run directory folders, each with name ``SimulationName_FourDigitEnsembleMemberID``. These are standard GEOS-Chem run directories, copied from the Template Run Directory. The only difference between these ensemble members and other run directories are that these lack individual run scripts. In addition, ``HEMCO_Config.rc`` is linked to NetCDF files containing gridded scaling factors which are updated at assimilation time. Unique instances of these scaling factors are present in each of these folders and have names of form ``*_SCALEFACTOR.nc``.
 * **Warning: Do not create any additional directories within the Ensemble Runs folder.** CHEEREIO will fail at assimilation time if there is an unexpected directory within the Ensmble Runs directory.

