# A package to handle time related routines (but not JD <-> date
# conversions)
#
# Author: Patricio F. Ortiz
# Date:   Sometime at the begining of 2017 AD

package ap_timex;

use strict;
use Time::Local;
use Date::Parse;



my @timeUnits = qw(day month year century hour minute second);
my @daysInMond = qw(0 31 28 31 30 31 30 31 31 30 31 30 31);
my @monthsInWords = qw(dummy January February March April May June July August September October November December);

use Exporter qw(import);
 
#our @EXPORT_OK = qw(isLeap equivDateDoy dateToDoy listOfDates daysInMonth daysInYear todayInDoy datesBetween segmentedDates getListOfDates);

our @EXPORT = qw(isLeap equivDateDoy dateToDoy listOfDates daysInMonth daysInYear todayInDoy datesBetween segmentedDates getListOfDates getSpecialDates getUTCat00);
 
 
# get the list of dates in a valid date-string
#
# New feature is to add time resolution to the input string in the form:
# Thu Mar 30 09:19:40 BST 2017
#
# Motivation:
# One does not always want to have a list of days, many times one needs
# just a list of years, or a list of months or even a list of HHMM
# following the date at a certain interval (eg, every 5 minutes)
#
# Solution:
# - add "/dt=xUNIT" at the end of the string to specify a different interval
# - make the default time resolution to be "/dt=1day"
# - valid UNIT:  day month year hour minute
#
# when UNIT is year or month or day, the interval is ignored
#
sub getListOfDates(){
    my $lod = shift;
    my $_;
#    my $_ = @_[0];
    my ($interval, $date, $unit, $theDateString, $unit);
    my @parts = split(/\//, $lod);
    if(!$lod =~ /\/dt=/){
        $interval = "dt=1day";
        $theDateString = $lod;
    } else {
        $date = $lod;
#        print "Splitting: $lod\n";
        ($theDateString, $interval) = split(/\//, $lod);
    }
    $interval =~ s/dt=//;
    $_ = lc($interval);
#    print "Interval: $interval\n";
#    print "dateString: $theDateString\n";
    my $dtUnit = "";
    my $dtValue = 0;
    my @pdate;
    my $year;
    my $month;
    my $day;
    foreach $unit (@timeUnits){
        if(/$unit/){
            $dtUnit = $unit;
            $_ =~ s/$unit//;
            $dtValue = $_;
            last;
        }
    }
#    print "Interval:  $dtValue $dtUnit\n";
    if($dtValue == 0 or $dtUnit eq ""){
        die "Invalid time-resolution syntax for string $_[0]\n";
    }
    my @LISTOFDATES;
    $_ = $theDateString;
    if(/\@/){        # we've got a segmented range of dates
        @LISTOFDATES = &segmentedDates($_, "-");
    } elsif(/:/){        # we've got a full range of dates
        my ($firstDate, $lastDate ) = split(/:/,$_);
#        print "From $firstDate to $lastDate\n";
        if($firstDate ne "" and $lastDate ne ""){
            my($xy, $xm, $xd);
            ($xy, $xm, $xd) = split(/-/, $firstDate);
            if($xm eq ""){ $xm = "01"; }
            if($xd eq ""){ $xd = "01"; }
            $firstDate = "${xy}-${xm}-${xd}";

            ($xy, $xm, $xd) = split(/-/, $lastDate);
            if($xm eq ""){ $xm = "12"; }
            if($xd eq ""){
                $xd = $daysInMond[int($xm)];
            }
            $lastDate = "${xy}-${xm}-${xd}";

            @LISTOFDATES = &datesBetween($firstDate, $lastDate, "-");
#            @LISTOFDATES = &datesBetween("$year-1-1", "$year-12-31", "-");
        }  else {
            die "Invalid date format. For a range specify:   date1:date2\n";
        }
    
    } elsif(/,/){   # we've got a list of user defined dates
        @LISTOFDATES = split(/,/);
    } else {        # it is a simple date, but it could involve a range of dates
                    # as well
        @pdate = split(/-/);
        $year  = shift(@pdate);
        $month = shift(@pdate);
        $day   = shift(@pdate);
        
        my $imonth = int($month);
        my $lmonth = $monthsInWords[$imonth];
        my $iday = int($day);
        my $smonth = sprintf("%02d", $imonth);
        my $sday = sprintf("%02d", $iday);
        
        if($day eq "" and $month eq ""){
            @LISTOFDATES = &datesBetween("$year-1-1", "$year-12-31", "-");
        } elsif ( $day eq "" and $month ne ""){
            my $DAYSINMONTH = &daysInMonth($year, $imonth);
            @LISTOFDATES = &datesBetween("$year-$month-1", "$year-$month-$DAYSINMONTH", "-");
        } else {
            push @LISTOFDATES, $_;
        }
    }
    
    # at this point, when we already have a list of days, we apply other
    # criteria according to the unit chosen
    if($dtUnit eq "day") { # ready to return :-)
        return @LISTOFDATES;
    } elsif($dtUnit eq "year"){
        my %years;
        foreach $_ (@LISTOFDATES){
            ($year, $month, $day) = split(/-/);
            $years{"${year}"} = 1;
        }
        my @ylist = sort keys %years;
        return @ylist;
    } elsif($dtUnit eq "month"){
        my %months;
        foreach $_ (@LISTOFDATES){
            ($year, $month, $day) = split(/-/);
            $months{"${year}-${month}"} = 1;
        }
        my @mlist = sort keys %months;
        return @mlist;
    } elsif($dtUnit eq "hour"){
        my @hours;
        my $firstHour = 0;
        my ($hour, $sour);
#        print "dtValue: $dtValue\n";
#        print "LOD: @LISTOFDATES\n";
        foreach $_ (@LISTOFDATES){
#            print "Dealing with date: $_\n";
            for($hour = $firstHour; $hour < 24; $hour += $dtValue){
#                print "Hour: $hour\n";
                $sour =  sprintf("${_}T%02d0000", $hour);
                push @hours, $sour;
            }
        }
        return @hours;
    } elsif($dtUnit eq "minute"){
        my @minutes;
        my $firstHour = 0;
        my ($minute, $sour, $h, $m);
#        print "dtValue: $dtValue\n";
#        print "LOD: @LISTOFDATES\n";
        foreach $_ (@LISTOFDATES){
#            print "Dealing with date: $_\n";
            for($minute = $firstHour; $minute < 1440; $minute += $dtValue){
#                print "Hour: $minute\n";
                $h = int($minute/60);
                $m = int($minute % 60);
                $sour =  sprintf("${_}T%02d%02d00", $h, $m);
                push @minutes, $sour;
            }
        }
        return @minutes;
    } elsif($dtUnit eq "second"){
        my @seconds;
        my $firstHour = 0;
        my ($second, $sour, $h, $m, $left);
#        print "dtValue: $dtValue\n";
#        print "LOD: @LISTOFDATES\n";
        foreach $_ (@LISTOFDATES){
#            print "Dealing with date: $_\n";
            for($second = $firstHour; $second < 86400; $second += $dtValue){
#                print "Hour: $second\n";
                $left = $second;
                $h = int($second/3600);
                $left -= $h*3600;
                $m = int($left / 60);
                $left -= $m*60;
                $sour =  sprintf("${_}T%02d%02d%02d", $h, $m,$left);
                push @seconds, $sour;
            }
        }
        return @seconds;
    } 
}

# returns the current year and the current doy
sub todayInDoy(){
    my( $hsec, $hmin, $hhour, $hmday, $hmon, $hyear, $hwday, $hyday, $hisdst) = localtime();
    $hyday++;
    $hyear += 1900;
#    $hmon++;
#    my $doy = &dateToDoy($hyear, $hmon, $hmday);
#    print "TIMEX: doy=$doy hyday=$hyday\n";
    return ($hyear, $hyday);
}

sub isLeap {
    my ($year) = @_;
    my $leap = 0;
    if(($year%4) == 0 && ( ($year%100 != 0) || ($year%400 == 0) ) ){
        $leap =1;
    }

    return $leap;
}
 
sub daysInMonth {
    my ($year, $month) = @_;
    my @dom;
    foreach $_ (@daysInMond){ push @dom, $_; }
    if(&isLeap($year) == 1){
        $dom[2] = 29;
    } else {
        $dom[2] = 28;
    }
    my $daysInMonth = $dom[$month];
    return $daysInMonth;
}
 
sub daysInYear {
    my ($year,@rest) = @_;
    my $daysInJahre = 365;
    if(&isLeap($year) == 1){
        $daysInJahre++;
    }
    return $daysInJahre;
}
 
sub equivDateDoy {
    my ($year) = @_;
    my @dom;
    foreach $_ (@daysInMond){ push @dom, $_; }
    if(&isLeap($year) == 1){
        $dom[2] = 29;
    } else {
        $dom[2] = 28;
    }
    my ($doy,  $mon,  $day);
    my ($sdoy, $smon, $sday);
    $doy = 0;
    my ($m_, $d_, $date);
    my $nim;
    my %eqDateDoy;
    for($m_ = 1; $m_ < 13; $m_++){
        $nim = $dom[$m_];
        $smon = sprintf("%02d", $m_);
        for($d_ = 1; $d_ <= $nim; $d_++){
            $sday = sprintf("%02d", $d_);
            $doy++;
            $date  = "$smon/$sday";
            $sdoy = sprintf("%03d", $doy);
            $eqDateDoy{$date} = $sdoy;
        }
    }
    return %eqDateDoy;
}
 
# transforms a date (year/month/day) into a day-of-year value
sub dateToDoy{
    my ($year, $month, $day) = @_;
#    print "year/mm/dd = $year, $month, $day\n";
    my %edd = &equivDateDoy($year);
    my $date = sprintf("%02d/%02d",$month,$day);
#    print "$date\n";
#    my @kles = sort keys %edd;
#    print "@kles\n";
    return $edd{$date};
}

# Returns the list of days in a single year
sub listOfDates {
    my ($year, $sep, $incYear) = @_;
    my @dom;
    foreach $_ (@daysInMond){ push @dom, $_; }
    if(&isLeap($year) == 1){
        $dom[2] = 29;
    } else {
        $dom[2] = 28;
    }
    my ($doy,  $mon,  $day);
    my ($sdoy, $smon, $sday);
    $doy = 0;
    my ($m_, $d_, $date);
    my $nim;
    my @lodays;
    for($m_ = 1; $m_ < 13; $m_++){
        $nim = $dom[$m_];
        $smon = sprintf("%02d", $m_);
        for($d_ = 1; $d_ <= $nim; $d_++){
            $sday = sprintf("%02d", $d_);
            $doy++;
            if($incYear == 1){
                $date  = "${year}${sep}${smon}${sep}${sday}";
            } else {
                $date  = "${smon}${sep}${sday}";
            }
            push @lodays, $date;
#            $sdoy = sprintf("%02d", $doy);
#            $eqDateDoy{$date} = $sdoy;
        }
    }
    return @lodays;
}
 
# list all dates between two dates (inclusive)
# arguments: initialDate, finalDate, separator
sub datesBetween {
    my ($initialDate, $finalDate, $sep) = @_;
    my @domi;
    my @domj;
    my @domf;
    my ($iyear, $imonth, $iday);
    my ($fyear, $fmonth, $fday);

    foreach $_ (@daysInMond){
        push @domi, $_;
        push @domj, $_;
        push @domf, $_;
    }   
#    print "Separator >$sep<\n";
    $_ = $initialDate;
    $_ =~ m/[^0-9]/p;
    my $mid = ${^MATCH};
    if($mid ne ""){
        ($iyear, $imonth, $iday) = split(/$mid/);
        $imonth = int($imonth);
        $iday = int($iday);
    } else {
        $iyear=$initialDate;
        $imonth = 1;
        $iday = 1;
    }
    if(&isLeap($iyear) == 1){
        $domi[2] = 29;
    } else {
        $domi[2] = 28;
    }
    if($iday eq ""){ $iday = 1; }
#    print "$initialDate $mid $iyear $imonth $iday\n";
    my (%inDay, %inMonth, %finDay, %finMonth);
    my $key;
    $inDay{"$iyear $imonth"} = $iday;
    $inMonth{$iyear} = $imonth;
    $_ = $finalDate;
    $_ =~ m/[^0-9]/p;
    $mid = ${^MATCH};
    if($mid ne ""){
        ($fyear, $fmonth, $fday) = split(/$mid/);
        $fmonth = int($fmonth);
        $fday = int($fday);
    } else {
        $fyear=$initialDate;
        $fmonth = 12;
        $fday = 31;
    }
    if(&isLeap($fyear) == 1){
        $domf[2] = 29;
    } else {
        $domf[2] = 28;
    }
    if($fday eq ""){ $fday = $domf[$fmonth]; }
    $finDay{"$fyear $fmonth"} = $fday;
    $finMonth{$fyear} = $fmonth;
#    print "$initialDate $mid $fyear $fmonth $fday\n";
    
    my ($jahre, $mond, $iMond, $fMond, $tagh, $iTag, $fTag );
    my (@lodates, $sdate);
    for($jahre = $iyear; $jahre <= $fyear; $jahre++){
        if(&isLeap($jahre) == 1){
            $domj[2] = 29;
        } else {
            $domj[2] = 28;
        }
        if($inMonth{$jahre} eq ""){
            $iMond = 1;
        } else {
            $iMond = $inMonth{$jahre};
        }
        if($finMonth{$jahre} eq ""){
            $fMond = 12;
        } else {
            $fMond = $finMonth{$jahre};
        }
        for($mond = $iMond; $mond <= $fMond; $mond++){
#            print "$jahre $mond\n";
            $key = "$jahre $mond";
            if($inDay{$key} eq ""){
                $iTag = 1;
            } else {
                $iTag = $inDay{$key};
            }
            if($finDay{$key} eq ""){
                # new dom for the jahre needs to be computed
                $fTag = $domj[$mond];
            } else {
                $fTag = $finDay{$key};
            }
            for($tagh = $iTag; $tagh <= $fTag; $tagh++){
                $sdate = sprintf("%04d%s%02d%s%02d",$jahre, $sep, $mond, $sep, $tagh);
#                print "$jahre $mond $tagh\n";
#                print "$sdate\n";
                push @lodates, $sdate;
            }
        }
    }

    return @lodates;

}
 
 
# list all dates involving selected months for a number of selected years
# arguments: dateString separator
sub segmentedDates {
    my ($dateString, $sep) = @_;

    my ($month_c, $year_c) = split(/\@/,$dateString);
    # Do we have a single month, a list of months or a range of months?
    # In all cases, we obtain a list of months.
    my ($amon, $mon1, $mon2);
    my $_ = $month_c;

    my @months;
    if(/:/){        # we got a range of months
        ($mon1, $mon2) = split(/:/);
        for($amon = $mon1; $amon <= $mon2; $amon++){
            push @months, $amon;
        }
    } elsif(/,/){   # we got a few months
        @months = split(/,/);
    } else {                    # we got a single month
        push @months, $_;
    } 
#    print " Months: @months\n";
    my @years;
    $_ = $year_c;
    if(/:/){        # we got a range of years
        ($mon1, $mon2) = split(/:/);
        for($amon = $mon1; $amon <= $mon2; $amon++){
            push @years, $amon;
        }
    } elsif(/,/){   # we got a few years
        @years = split(/,/);
    } else {                    # we got a single year
        push @years, $_;
    } 
#    print " Years @years\n";
    my ($jahre, $mond, $timo, $sday);
    my (@lodates, $sdate);
    foreach $jahre (@years){
        foreach $mond (@months){
            $timo = &daysInMonth($jahre, $mond);
            for($sday = 1; $sday <= $timo; $sday++){
                 $sdate = sprintf("%04d%s%02d%s%02d",$jahre, $sep, $mond, $sep, $sday);
                 push @lodates, $sdate;
            }
        }
    }
    return @lodates;

}
 
# produce a list of dates based on a time directive
sub getSpecialDates(){
    my $directive = shift;
    my $initialTime = time; # time in unix time-stamp
    my @lodates;
    my ($D_sec,$D_min,$D_hour,$D_mday,$D_mon,$D_year,$D_wday,$D_yday,$D_isdst);
    my ($yy, $mm, $dd);
    print "TimeStamp: $initialTime\n";
    if($directive eq "today-local-time"){
        ($D_sec,$D_min,$D_hour,$D_mday,$D_mon,$D_year,$D_wday,$D_yday,$D_isdst) = localtime($initialTime);
    } elsif($directive eq "yesterday-local-time"){
        $initialTime -= 86400;
        ($D_sec,$D_min,$D_hour,$D_mday,$D_mon,$D_year,$D_wday,$D_yday,$D_isdst) = localtime($initialTime);
    } elsif($directive eq "tomorrow-local-time"){
        $initialTime += 86400;
        ($D_sec,$D_min,$D_hour,$D_mday,$D_mon,$D_year,$D_wday,$D_yday,$D_isdst) = localtime($initialTime);
    } elsif($directive eq "today-universal-time"){
        ($D_sec,$D_min,$D_hour,$D_mday,$D_mon,$D_year,$D_wday,$D_yday,$D_isdst) = gmtime($initialTime);
#        print gmtime($initialTime) . "\n";
    } elsif($directive eq "yesterday-universal-time"){
        $initialTime -= 86400;
        ($D_sec,$D_min,$D_hour,$D_mday,$D_mon,$D_year,$D_wday,$D_yday,$D_isdst) = gmtime($initialTime);
    } elsif($directive eq "tomorrow-universal-time"){
        $initialTime += 86400;
        ($D_sec,$D_min,$D_hour,$D_mday,$D_mon,$D_year,$D_wday,$D_yday,$D_isdst) = gmtime($initialTime);
    } else {
        print "invalid time directive: $directive. Execution halted\n";
        exit;
    }
    $yy = $D_year + 1900;
    $mm = $D_mon + 1;
    $dd = $D_mday;

    push @lodates, sprintf("%04d-%02d-%02d", $yy, $mm, $D_mday);
    return @lodates;
}

 
# returns a timestamp for the current date (GMT) at midnight and the
# current number of seconds since that moment
sub getUTCat00(){
    my $initialTime = time; # time in unix time-stamp
    my @lodates;
    my ($yy, $mm, $dd);
    my
    ($D_sec,$D_min,$D_hour,$D_mday,$D_mon,$D_year,$D_wday,$D_yday,$D_isdst) = localtime($initialTime);

    my $midnight = sprintf("%04d-%02d-%02dT00:00:00", $D_year+1900, $D_mon+1,
$D_mday);

    my $utc0000 =  str2time($midnight);
    print "currentTime: $initialTime\n";
    print "midnight: $midnight $utc0000\n";
    my $nsec = int($initialTime - $utc0000);

    return $utc0000, $nsec;
}

1;
