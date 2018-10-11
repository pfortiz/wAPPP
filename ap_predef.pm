# perl module to contain predefined tasks definitions, used mostly by
# AP_assistant and AP_aurora
package ap_predef;

use strict;

my %pdtx; # pdtexplanation;
my %pdtf; # pdtNumericFlag;
my @pdtp; # pdtPrefixes

@pdtp = qw(dlftp proc dqc dxst ulftp rsync ud spwn dharv);

$pdtx{"dlftp"} = "a task dealing with ftp data acquisition";
$pdtx{"proc"} = "a task dealing with data processing";
$pdtx{"dqc"} = "a task dealing with data validation";
$pdtx{"dxst"} = "a task to verify if data exists";
$pdtx{"ulftp"} = "a task dealing with ftp uploads to a remote site";
$pdtx{"rsync"} = "a task to transfer data (upload/download) using rsync";
$pdtx{"spwn"} = "any task not to be run in parallel";
$pdtx{"dharv"} = "a task dealing with data harvesting";
$pdtx{"ud"} = "a task not defined above. To be defined from scratch.";
#$pdtx{"TB_*"} = "a task present in user-defined TaskBlock directories.";

$pdtf{"dlftp"} = 1;
$pdtf{"proc"} = 2;
$pdtf{"dqc"} = 4;
$pdtf{"dxst"} = 8;
$pdtf{"ulftp"} = 16;
$pdtf{"rsync"} = 32;
$pdtf{"spwn"} = 64;
$pdtf{"dharv"} = 128;
#$pdtf{"TB_*"} = 256;
$pdtf{"ud"} = 256;


my @daysInMond = qw(0 31 28 31 30 31 30 31 31 30 31 30 31);
my @monthsInWords = qw(dummy January February March April May June July August September October November December);

use Exporter qw(import);
 
our @EXPORT_OK = qw(pexp cexp getAPflags getAPtypes);

our @EXPORT = qw(pexp cexp getAPflags getAPtypes validateTask locateTBlegos);

#check whether the task suffix is correct
sub validateTask(){
    my $task = shift;
    my %logos = shift;
    my $k;
    my %locLegos = {};
    foreach $k (keys %main::legos){
#        print "DEF lego: $k\n";
        $locLegos{$k} = 1;
    }
    my ($prefix, $tname) = split(/-/, $task);
    if($pdtx{$prefix} eq ""){
        print "PREFIX: $prefix\n";
        if($locLegos{$prefix} eq ""){
            print "no PREFIX: $prefix\n";
            return 0;
        } else {
            print "yes PREFIX: $prefix\n";
            return 1;
        }
    } else {
        return 1;
    }
}
 
sub locateTBlegos(){
    my $pPath = @_[0];
    my %legos = {};
    my @pp;
#    print "LEGOS in $pPath\n";
    open(P, "ls $pPath|");
    while(<P>){
        if(/TB_/){
#            print "LEGO found: $_\n";
            chop;
            $legos{$_} = "$pPath/$_";
        }
    }
    # addition on October 10, 2018 to account for the fact that TBlegos
    # could be located in different paths, and these paths are listed in
    # the AP_project file in the current directory.
    open(AP, "<AP_project");
    while(<AP>){
        if(/tbPaths/){
            chop;
            my ($prefix, $paths) = split(/=/);
            @pp = split(/;/, $paths);
            foreach $pPath (@pp){
                print "Scanning $pPath for TB_s\n";
                if(-e $pPath){
                    open(P, "ls $pPath|");
                    while(<P>){
                        if(/TB_/){
                            chop;
                            print "LEGO found: $_\n";
                            $legos{$_} = "$pPath/$_";
                        }
                    }
                }
            }
        }
    }
    close(AP);
    return %legos;
}

sub pexp(){
    my $explain = "";
    foreach $_ (keys %pdtx){
        $explain .= sprintf("%-6s = %s\n", $_."-", $pdtx{$_});
    }
    return $explain;
}

sub cexp(){
    my $explain = "";
    foreach $_ (sort keys %pdtx){
        $explain .= sprintf("# %-6s = %s\n", $_."-", $pdtx{$_});
    }
    return $explain;
}

sub getAPflags(){
    return %pdtf;
}

sub getAPtypes(){
    return @pdtp;
}

1;


