# perl module to contain predefined tasks definitions, used mostly by
# AP_assistant and AP_aurora
package ap_predef;

use strict;

my %pdtx; # pdtexplanation;
my %pdtf; # pdtNumericFlag;
my @pdtp; # pdtPrefixes

@pdtp = qw(dlftp proc dqc dxst ulftp rsync ud);

$pdtx{"dlftp"} = "a task dealing with ftp data acquisition";
$pdtx{"proc"} = "a task dealing with data processing";
$pdtx{"dqc"} = "a task dealing with data validation";
$pdtx{"dxst"} = "a task to verify if data exists";
$pdtx{"ulftp"} = "a task dealing with ftp uploads to a remote site";
$pdtx{"rsync"} = "a task to transfer data (upload/download) using rsync";
$pdtx{"spwn"} = "any task not to be run in parallel";
$pdtx{"ud"} = "a task not defined above. To be defined from scratch.";

$pdtf{"dlftp"} = 1;
$pdtf{"proc"} = 2;
$pdtf{"dqc"} = 4;
$pdtf{"dxst"} = 8;
$pdtf{"ulftp"} = 16;
$pdtf{"rsync"} = 32;
$pdtf{"spwn"} = 64;
$pdtf{"ud"} = 255;


my @daysInMond = qw(0 31 28 31 30 31 30 31 31 30 31 30 31);
my @monthsInWords = qw(dummy January February March April May June July August September October November December);

use Exporter qw(import);
 
our @EXPORT_OK = qw(pexp cexp getAPflags getAPtypes);

our @EXPORT = qw(pexp cexp getAPflags getAPtypes);
 
 
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


