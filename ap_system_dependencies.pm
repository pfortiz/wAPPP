# A package to bundle all system dependencies used in wAPPP in one place,
# so that adding new sites or situations becomes simple, affecting only
# this script.
#
#
# Author: Patricio F. Ortiz
# Date:   Started 09 July 2017 AD

package ap_system_dependencies;

use strict;


my @timeUnits = qw(day month year century hour minute second);
my @daysInMond = qw(0 31 28 31 30 31 30 31 31 30 31 30 31);
my @monthsInWords = qw(dummy January February March April May June July August September October November December);

use Exporter qw(import);
 
#our @EXPORT_OK = qw(isLeap equivDateDoy dateToDoy listOfDates daysInMonth daysInYear todayInDoy datesBetween segmentedDates getListOfDates);

our @EXPORT = qw(getFromRc);
 
# this routine does not set anything according to the system it is in, but
# it extract information from the user's .rc file

sub getFromRc(){
#    my $file = @_[0];
    my $home = $ENV{HOME};
    my $rcfile = "$home/.automatedProcessing";

    my %rcDict;
    if(!-e $rcfile){
        &createRc();
        print "$rcfile created. Please review its contents\n";
        exit;
    }
    open(F, "<$rcfile");
    while(<F>){
        if(/^#/ or /^$/){ next; }
        chop;
        my ($key, $value) = split(/=/,$_,2);
        $rcDict{$key} = "$value";
    }
    close(F);
    return %rcDict;
}


sub createRc(){
    my $home = $ENV{HOME};
    my $rcfile = "$home/.ottomatedProcessing";
    my $host = `hostname`;
    chop ($host);
    my $home = $ENV{HOME};
    my @parts = split(/\//, $0);
    pop @parts;
    my $myPath = join("/", @parts);

    my ($site, $history, $basePath, $exec_path, $tctl_path, $bundlePath);
    my ($qtag, $pythonx, $qsubmit, $qdelete, $qquery, $err_memory);
    my ($err_walltime);
    if(($host =~/alice/) or ($host=~/spectre/)){
        $site = "UOL";
        $history = "GT_HISTORY";
        $basePath = "/data/atsr";
        $exec_path = "$basePath/SOFTWARE/FORTRAN/INTERNAL_CODE/BIN";
        $tctl_path = "$basePath/SOFTWARE/FORTRAN/INTERNAL_CODE/CTL_FILES_TEMPLATES";
        $bundlePath = "$basePath/SOFTWARE/SCRIPTS/AUTOMATED_PROCESSING";
        $qtag = "PBS";
        $pythonx = "python";
        $qsubmit = "qsub -W x=resfailpolicy:requeue";
        $qdelete = "qdel";
        $qquery = "qstat";
        $err_memory = "Cannot allocate memory";
        $err_walltime = "job killed: walltime";
    } elsif($host =~/rl.ac.uk/){
        $site = "CEMS";
        $history = "GT_HISTORY";
        $basePath = "/group_workspaces/cems/leicester";
        $bundlePath = "$basePath/SOFTWARE/SCRIPTS/AUTOMATED_PROCESSING";
        $exec_path = "$basePath/SOFTWARE/FORTRAN/INTERNAL_CODE/BIN";
        $tctl_path = "$basePath/SOFTWARE/FORTRAN/INTERNAL_CODE/CTL_FILES_TEMPLATES";
        $pythonx = "python2.7";
        $qtag = "BSUB";
        $qsubmit = "bsub -r <";
        $qdelete = "bkill";
        $qquery = "bjobs";
        $err_memory = "job killed after reaching LSF memory usage limit.";
        $err_walltime = "job killed after reaching LSF run time limit";
    } elsif($host =~/acri.fr/){
        $site = "CTCP";
        $history = "GT_HISTORY";
        $basePath = "/a/trouver";
        $bundlePath = "$basePath/SOFTWARE/SCRIPTS/AUTOMATED_PROCESSING";
        $exec_path = "$basePath/SOFTWARE/FORTRAN/INTERNAL_CODE/BIN";
        $tctl_path = "$basePath/SOFTWARE/FORTRAN/INTERNAL_CODE/CTL_FILES_TEMPLATES";
        $pythonx = "python";
        $qtag = "BSUB";
        $qsubmit = "bsub ";
        $qdelete = "bkill";
        $qquery = "bjobs";
        $err_memory = "Pas suffi memoir";
        $err_walltime = "job killed after reaching LSF run time limit";
    } elsif($host =~/iceberg/ or $host =~/sharc/) {
        print "In Iceberg/sharc, University of Sheffield.\n";
        # this should be a path to install as a local installation
        $site = "UOS";
        $history = "ICY_HISTORY";
        $basePath = "$home";
        $bundlePath = "$myPath";
        $exec_path = "$basePath/bin";
        $tctl_path = "$basePath/ctl_files";
        $pythonx = "python";
        $qtag = "\$";
        $qsubmit = "qsub";
        $qdelete = "qdel";
        $qquery = "Qstat";
        $err_memory = "Can not allocate memory";
        $err_walltime = "job killed after reaching LSF run time limit";
    } else {
        print "In non-parallel system.\n";
        # this should be a path to install as a local installation
        $site = "nonParallel";
        $history = "AP_HISTORY";
        $basePath = "$home";
        $bundlePath = "$myPath";
        $exec_path = "$basePath/bin";
        $tctl_path = "$basePath/ctl_files";
        $pythonx = "python";
        $qtag = "disabled";
        $qsubmit = "ksub";
        $qdelete = "kdel";
        $qquery = "kstat";
        $err_memory = "Kein Memory";
        $err_walltime = "job killed after reaching LSF run time limit";
    }


    open(RC, ">$rcfile");
#        $bundlePath = "SOFTWARE/SCRIPTS/AUTOMATED_PROCESSING";
    print RC <<"RUNPIPELINERC";
# .automatedProcessing
# Mostly definitions which are site dependent

# This one can be UOL, CEMS, UOS, or something else to come
site=$site

# The path to where SOFTWARE/SCRIPTS is located
basePath=$basePath

# The full path to where this "package" is located
appath=$bundlePath

# The full path to where executables are to be found
exec_path=$exec_path

# The full path to where template control files are to be found
tctl_path=$tctl_path

# The path to where runPipe area is located
# You can change this path to suit your needs
historyPath=$basePath/$history

#---------------------------------------------------------------
# These definitions deal with parallel processing site-depending
# commands or error messages

# Tag that goes in the submission scripts
qtag=$qtag

# The queue submit command
qsubmit=$qsubmit

# The command to delete jobs from the queue
qdelete=$qdelete

# The command to query the queue-manager about which jobs are running
qquery=$qquery

wtError=$err_walltime
memError=$err_memory
python=$pythonx
RUNPIPELINERC
    close(RC);
}
