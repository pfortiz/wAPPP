# A package to bundle all system dependencies used in wAPPP in one place,
# so that adding new sites or situations becomes simple, affecting only
# this script.
#
#
# Author: Patricio F. Ortiz
# Date:   Started 09 July 2017 AD

package ap_system_dependencies;

use strict;


use Exporter qw(import);

our @EXPORT = qw(getFromRc getNavailableProcesses getRunningJobIds getProcessDict decHourToHHMM decHourToHHMMSS getSiteParams createQsubFile pipeStats);
 
#our @EXPORT_OK = qw(isLeap equivDateDoy dateToDoy listOfDates daysInMonth daysInYear todayInDoy datesBetween segmentedDates getListOfDates);

 
my @timeUnits = qw(day month year century hour minute second);
my @daysInMond = qw(0 31 28 31 30 31 30 31 31 30 31 30 31);
my @monthsInWords = qw(dummy January February March April May June July August September October November December);

# this routine does not set anything according to the system it is in, but
# it extract information from the user's .rc file
# If the .rc file does not exist, then it invokes createRc, which does
# define parameters according to the system.

# %dict = getFromRc();
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


# This routine creates the .rc file based on the system it is in.
sub createRc(){
    my $home = $ENV{HOME};
    my $rcfile = "$home/.automatedProcessing";
    my $host = `hostname`;
    chop ($host);
    my $home = $ENV{HOME};
    my @parts = split(/\//, $0);
    pop @parts;
    my $myPath = join("/", @parts);
    if($myPath eq "."){
        $myPath = `pwd`;
        chop($myPath);
    }

    my ($site, $history, $basePath, $exec_path, $tctl_path, $bundlePath);
    my ($qtag, $pythonx, $qsubmit, $qdelete, $qquery, $err_memory);
    my ($err_walltime, $machine);

    $machine = `uname`;
    chop($machine);

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
        $qquery = "qstat";
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

# the kind of machine this is running from:
machine=$machine
RUNPIPELINERC
    close(RC);
}


# nAvailableProcesses = getNavailableProcesses();
sub getNavailableProcesses(){
    my %dict = @_[0];
    my $uname = $ENV{USER};
    my $maxProcesses = `ulimit -u`;
    chop $maxProcesses;
    my $activeProcesses = 0;
    open(P, "ps -e -o user|");
    while(<P>){
        if(/$uname/){
            $activeProcesses++;
        }
    }
    close(P);
    my $availableProcesses = $maxProcesses - $activeProcesses;
    return $availableProcesses;
}


# routine to obtain a listing of jobs in the current queue of a parallel
# system. Thoughts need to be given on how to treat non-parallel systems.

# syntax: @arrayOfPointers = getRunningJobIds( $dummy, %dict);
sub getRunningJobIds(){
    my (%dict) = @_;
    my $site = $dict{"site"};
    print "Utilizing site: $site\n";

    my %runningJobs;
    my $qquery = $dict{"qquery"};
    my @errorFiles;
    my %errorsById;
    my %logsById;
    my %runningJobs;

    open(Q, "$qquery | ");
    my $nJobsRunning = 0;
    my (@jobs, $jid, $status, @lepath, $eid, $oid);
    if($site eq "UOL"){
        $_ = <Q>;       # dummy line
        $_ = <Q>;       # dummy line
        while(<Q>){
            chop;
            @jobs = split();
            $jid = shift(@jobs);
            $status = $jobs[3];
#            if($status ne "C"){
#            }
            $runningJobs{$jid} = 1;
            $nJobsRunning++;
            print "QRJ: $jid\n";
        } 
        # how do I distinguish an error in the queue system from a real
        # situation when no jobs are running??
        # we are at $dotOdotE   Which files are there?
        open(E, "ls  | ");
        while(<E>){
            chop;
            if(/\.e/){
                push @errorFiles, $_;
                @lepath = split(/\.e/);
                $eid = $lepath[1];
                $errorsById{$eid} = $_;

#                print "Error file: $_\n";
            } elsif (/\.o/){
                @lepath = split(/\.o/);
                $oid = $lepath[1];
                $logsById{$oid} = $_;
            }
        }
        close(E);
        
    } elsif($site eq "CEMS"){
        # this needs fixing...
        $_ = <Q>;       # dummy line
        $_ = <Q>;       # dummy line
        while(<Q>){
            chop;
            @jobs = split();
            $jid = shift(@jobs);
            $status = $jobs[3];
#            if($status ne "C"){
#            }
            $runningJobs{$jid} = 1;
            $nJobsRunning++;
            print "QRJ: $jid\n";
        } 
        # how do I distinguish an error in the queue system from a real
        # situation when no jobs are running??
        # we are at $dotOdotE   Which files are there?
        open(E, "ls  | ");
        while(<E>){
            chop;
            if(/\.e/){
                push @errorFiles, $_;
                @lepath = split(/\.err/);
                $eid = $lepath[0];
                $errorsById{$eid} = $_;

#                print "Error file: $_\n";
            } elsif (/\.l/){
                @lepath = split(/\.log/);
                $oid = $lepath[0];
                $logsById{$oid} = $_;
            }
        }
        close(E);
        
    } elsif($site eq "CTCP"){
        # Totally pending...

    } elsif($site eq "UOS"){
        # I still don't know how this is handled here. I will assume that
        # this is like in the UOL case, ie, JobID.e and JOBID.o
        $_ = <Q>;       # dummy line
        $_ = <Q>;       # dummy line
        while(<Q>){
            chop;
            @jobs = split();
            $jid = shift(@jobs);
            $status = $jobs[3];
#            if($status ne "C"){
#            }
            $runningJobs{$jid} = 1;
            $nJobsRunning++;
            print "QRJ: $jid\n";
        } 
        # how do I distinguish an error in the queue system from a real
        # situation when no jobs are running??
        # we are at $dotOdotE   Which files are there?
        open(E, "ls  | ");
        while(<E>){
            chop;
            if(/\.e/){
                push @errorFiles, $_;
                @lepath = split(/\.e/);
                $eid = $lepath[1];
                $errorsById{$eid} = $_;

#                print "Error file: $_\n";
            } elsif (/\.o/){
                @lepath = split(/\.o/);
                $oid = $lepath[1];
                $logsById{$oid} = $_;
            }
        }
        close(E);
    } elsif($site eq "nonParallel"){
        # In this case there is nothing to query as there is no queue being
        # submitted.  The question is then, what to we return?
        # how do we get the PID of submitted jobs? Unless we submit them in
        # the background, then there is no point in checking them.
    }
    close(Q);
}


sub getProcessDict(){
    my $processingOutput = shift;
    my $site = shift;
    my $dask = shift;
    my $qjn = shift;
    my $queueJob = shift;
    my (@jobids, $jobsline, @jparts, %notInParallel, $jid);
    if($site eq "UOL"){
        @jobids = split(/\n/, $processingOutput);
        $jobsline = "";
        foreach $_ (@jobids){
            if(/JOB=/){
                $_ =~ s/JOB=//g;
            # this is how it works in ALICE
                $jobsline = $_;
            }
        }

        @jparts = split(/\./,$jobsline);
        if($jobsline eq ""){
            $notInParallel{$dask} = 1;
        } else {
            $queueJob->{$dask} = $jobsline;
            $qjn->{$dask} = $jparts[0];
            print "Jobs for $dask: $jobsline $jparts[0]\n";
        }
    } elsif($site eq "UOS"){
        # To be determined in Sharc or Iceberg
        @jobids = split(/\n/, $processingOutput);
        $jobsline = "";
        foreach $_ (@jobids){
            if(/JOB=/){
                $_ =~ s/JOB=//g;
            # this is how it works in ALICE
                $jobsline = $_;
            }
        }

        @jparts = split(/\./,$jobsline);
        if($jobsline eq ""){
            $notInParallel{$dask} = 1;
        } else {
            $queueJob->{$dask} = $jobsline;
            $qjn->{$dask} = $jparts[0];
            print "Jobs for $dask: $jobsline $jparts[0]\n";
        }
    } elsif($site eq "CEMS"){
        $_ = $processingOutput;
        @jobids = split(/[<>]/);
        $jid = $jobids[1];

        $qjn->{$dask} = $jid;
        $queueJob->{$dask} = $jid;
        print "JOBID\@CEMS = $jid\n";
    }
}

# subroutine to extract some parameters according to the site's syntax.
sub getSiteParams(){
    my $site = shift;
    my $clWalltime = shift;

    my ($walltime, $wallPat, $wallString, $submit);

    if($site eq "CEMS"){
        $walltime = &decHourToHHMM($clWalltime);
        $wallPat = "walltime=";
        $wallString = "#BS -l walltime=$walltime";
        $submit = "bsub < ";
    }   elsif($site eq "UOL"){
        $walltime = &decHourToHHMMSS($clWalltime);
        $wallPat = "walltime=";
        $wallString = "#PBS -l walltime=$walltime";
        $submit = "qsub ";
    }   elsif($site eq "CTCP"){
        $walltime = &decHourToHHMMSS($clWalltime);
        $wallPat = "??walltime=";
        $wallString = "#??$ -l h_rt=$walltime";
        $submit = "??qsub ";
    }   elsif($site eq "UOS"){
        $walltime = &decHourToHHMMSS($clWalltime);
        $wallPat = "walltime=";
        $wallString = "#$ -l h_rt=$walltime";
        $submit = "qsub ";
    }
    return ($walltime, $wallPat, $wallString, $submit);

}

sub createQsubFile(){
    my $site = shift;
    my $queueFile = shift;
    my $qwalltime = shift;
    my $memory = shift;
    my $jobName = shift;
    my $touchIt = shift;
    my $qtag = shift;
    my $qsubmit = shift;

    open(B, ">$queueFile");

    my ($walltime, $canExecute, $submit, $queueName);
    $canExecute = 0;
    if($site eq "UOL"){
        $walltime = &decHourToHHMMSS($qwalltime);
        print B <<"HEADER";
#!/bin/bash
#
#$qtag -N ${jobName}
#$qtag -l walltime=$walltime
#$qtag -l pvmem=${memory}mb
#$qtag -l procs=1
$touchIt
HEADER
#        if($mode eq "monthly"){
#            print B "#$qtag -t [1-$DAYSINMONTH]\n";
#        }
#        if($mode eq "yearly"){
#            print B "#$qtag -t [1-$DAYSINYEAR]\n";
#        }
        $canExecute = 1;
#        print "Emma: $tStepsShrt $qrunid\n";
#        if($mode eq "WAIT"){
#            print B "$tStepsShrt $qrunid\ntouch $marker\n";
#        } else {
#            print B "$tStepsShrt $qrunid\n";
#        }
        close(B);
        
        # Now, we need to wait for the marker to indicate completion
        $submit = "qsub $queueFile";
    } elsif($site eq "CEMS"){
        if($walltime < 24){
            $queueName = "short-serial";
        } else {
            $queueName = "long-serial";
        }
#        $jobName =  "${procedureId}-${loopycounter}";
        $walltime = &decHourToHHMM($qwalltime);
# TODO properly. queue name depends on walltime now
        my $memoryInKbytes = $memory * 1000;
        print B <<"HEADER";
#!/bin/bash
#
#$qtag -q $queueName
#$qtag -o %J.log
#$qtag -e %J.err
#$qtag -R "rusage[mem=$memory]"
#$qtag -M $memoryInKbytes
#$qtag -n 1
#$qtag -W $walltime
#$qtag -J ${jobName}
$touchIt
HEADER

#        if($mode eq "monthly"){
#            print B "#$qtag -t [1-$DAYSINMONTH]\n";
#        }
#        if($mode eq "yearly"){
#            print B "#$qtag -t [1-$DAYSINYEAR]\n";
#        }
        $canExecute = 1;
#        if($mode eq "WAIT"){
#            print B "$tStepsShrt $qrunid\ntouch $marker\n";
#        } else {
#            print B "$tStepsShrt $qrunid\n";
#        }
        close(B);
        
        # Now, we need to wait for the marker to indicate completion
        $submit = "bsub <  $queueFile";
    } elsif($site eq "UOS"){
        $walltime = &decHourToHHMMSS($qwalltime);
        # this needs fixing
        print B <<"HEADER";
#!/bin/bash
#
#$qtag -N ${jobName}
#$qtag -l h_rt=$walltime
#$qtag -l pvmem=${memory}mb
#$qtag -l procs=1
$touchIt
HEADER
        $canExecute = 1;
        close(B);
        $submit = "qsub $queueFile";
    } else {
        # do nothing, we can not launch if we don't know which parallel
        # system we are launching to.
        # but we need to trace...
        $canExecute = 1;
        $submit = "echo 'bash $queueFile'";
    }

    return($submit, $canExecute);
}

# routine to convert decimal hours to HH:MM:SS notation
sub decHourToHHMMSS(){
    my $wt = @_[0];
    my $nsec = $wt * 3600;
    my $nh = int( $nsec / 3600);
    my $nleft = $nsec;
    $nleft -= $nh*3600;
    my $nm = int( ($nleft/60));
    $nleft -= $nm*60;
    my $ns = int($nleft);
    my $wally = sprintf("%02d:%02d:%02d", $nh, $nm, $ns);
    return $wally;
}

# routine to convert decimal hours to HH:MM notation
# This notation is used at CEMS queues
sub decHourToHHMM(){
    my $wt = @_[0];
    my $nsec = $wt * 3600;
    my $nh = int( $nsec / 3600);
    my $nleft = $nsec;
    $nleft -= $nh*3600;
    my $nm = int( ($nleft/60));
    my $wally = sprintf("%02d:%02d", $nh, $nm);
    return $wally;
}

sub pipeStats(){

    my $screech = shift;
    my $logFile = shift;
    my $site = shift;

    my (@jparts, $qfile, $njobs2kill, $job, %qsubPerJob, $nerrorFiles);
    my ($nMemExceeded, $nWallHits, $nBusError, $nOtherErrors, $jobid);
    my ($file, $jobid, $qsubFile, $efile, @dparts, $dateId, $nerrors);
    my (%failingMemoryNodes, @busError, %failingBuses, $fNode, @memoryFailes);
    my (@wallHits, %failingBusNodes, %failingWallNodes, @otherErrors);
    my (@otherErrorsText, @withErrors, @withoutErrors);

    open (J, "<$logFile");
    $njobs2kill = 0;
    if($site eq "UOL"){
        while(<J>){
            chop;
            if(/\.qsub$/){
                @jparts = split;
                $qfile = pop(@jparts);
            } elsif(/Submitted job/){
                @jparts = split;
                $job = pop(@jparts);
                $job =~ s/\..*//;
                $qsubPerJob{$job} = $qfile;
#                print "$_\nJob/qsub $job $qfile\n";
                $njobs2kill++;
            }
        }
    } elsif($site eq "CEMS"){
        while(<J>){
            chop;
            if(/\.qsub$/){
                @jparts = split;
                $qfile = pop(@jparts);
            } elsif(/Submitted job/){
                @jparts = split;
                $job = pop(@jparts);
                $job =~ s/\..*//;
                $qsubPerJob{$job} = $qfile;
                print "$_\nJob/qsub $job $qfile\n";
                $njobs2kill++;
            }
        }
    } elsif($site eq "CTCP"){
        # to be fixed 
        while(<J>){
            chop;
            if(/\.qsub$/){
                @jparts = split;
                $qfile = pop(@jparts);
            } elsif(/Submitted job/){
                @jparts = split;
                $job = pop(@jparts);
                $job =~ s/\..*//;
                $qsubPerJob{$job} = $qfile;
#                print "$_\nJob/qsub $job $qfile\n";
                $njobs2kill++;
            }
        }
    } elsif($site eq "UOS"){
        # to be fixed 
        while(<J>){
            chop;
            if(/\.qsub$/){
                @jparts = split;
                $qfile = pop(@jparts);
            } elsif(/Submitted job/){
                @jparts = split;
                $job = pop(@jparts);
                $job =~ s/\..*//;
                $qsubPerJob{$job} = $qfile;
#                print "$_\nJob/qsub $job $qfile\n";
                $njobs2kill++;
            }
        }
    } else {
    }
    close(J);
    open(S, "ls $screech/*.e*|");
    $nerrorFiles = 0;
    $nMemExceeded = 0;
    $nWallHits = 0;
    $nBusError = 0;
    $nOtherErrors = 0;
    while(<S>){
        chop;
        ($file, $jobid) = split(/\.e/);
        $qsubFile = $qsubPerJob{$jobid};
        $efile = $_;
        open(E, "<$_");
        # The first three lines are standard
        $_ = <E>;
        @dparts = split;
        $dateId = "$dparts[2] $dparts[3] $dparts[4]";
        $_ = <E>;
        $_ = <E>;
        $_ = <E>;
        @dparts = split;
        $fNode = $dparts[2];
        $nerrors = 0;
        while(<E>){
            chop;
            if(/^#/) { next;}   # ignore debugging lines
            if(/Cannot allocate memory/){
#                print "Mem.fail: $jobid qsub $qsubFile\n";
                push @memoryFailes, $qsubFile;
                $nMemExceeded++;
                $failingMemoryNodes{$fNode}++;
                $nerrors++;
            } elsif(/Allocation would exceed/){
                #ignore
            } elsif(/ls: cannot access/){
                #ignore
            } elsif(/unknown HPC/){
                #ignore
            } elsif(/to run parallel/){
                #ignore
            } elsif(/to run in parallel/){
                #ignore
            } elsif(/Bus error/){
                push @busError, $qsubFile;
                $failingBuses{$fNode}++;
                $failingBusNodes{$fNode}++;
                $nBusError++;
                $nerrors++;
            } elsif(/job killed/ and /walltime/ and /exceeded/){
#                print "wall.hit $jobid qsub $qsubFile\n";
#                print "cp ${qsubFile} ${qsubFile}R\n";
                push @wallHits, $qsubFile;
                $failingWallNodes{$fNode}++;
                $nWallHits++;
                $nerrors++;
            } else {
                push @otherErrors, $qsubFile;
                print "Other error:  $jobid $efile $_\n";
                push @otherErrorsText, $_;
                $nOtherErrors++;
                $nerrors++;
            }
        }
        if($nerrors > 0){
#            print "With errros: $efile\n";
            push @withErrors, $efile;
        } else {
            push @withoutErrors, $efile;
        }
        close(E);
        $nerrorFiles++;
    }
    close(S);
    print "Number of jobs in the task: $njobs2kill\n";
    print "Number of error files: $nerrorFiles\n";
    print "Number of memory fails: $nMemExceeded\n";
    print "Number of wall hits $nWallHits\n";
    print "Number of Bus error $nBusError\n";
    print "Number of other errors $nOtherErrors\n";
}

1;
