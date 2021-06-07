
COPY BRANCHED WELLS

Project
----------

To run this example, you will need a project with well branches.
You can add these branches to the emerald project with the following steps:

1. Find enclosed two files in RMS wells format ("OP1_B.rmswell", "OP2_B.rmswell").
   These define well branches for the two wells, OP1 and OP2, in the Emerald project.
   The branches are named OP1_B and OP2_B, respectively.

2. Import the two files into the Emerald project, using "RMS wells" format.
   Right-click Wells, select Tasks > Import > Wells Data; then select "RMS Well" format.
   Under select files, browse and select the two rmswell files.
   Select to add as a new well. Keep the other default settings. Click run.

   The wells will be imported as individual wells.
   The two branches are constructed to share survey points with the parent well, above the branch points.  

3. Rename the two imported trajectories from ‘Imported trajectory’ to ‘Drilled trajectory’.  


Branch Description
-------------------

The file "well_branches.txt" defines this branch structure.
This is intended as input for the "wells_copy_branches.py" Python script.


Python Script
------------------------

The "wells_copy_branches.py" script can be used to set up the two wells with 
branch structure in the Emerald project.


The python script calls the wells module from the Roxar API Utilities library.