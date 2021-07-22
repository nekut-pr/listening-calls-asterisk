#!/usr/bin/perl

use strict;
use warnings;

use utf8; 
use POSIX qw(strftime);
use CGI qw/:standard/;
use CGI::Carp qw(fatalsToBrowser);

binmode(STDOUT,':utf8');

my $cgi = new CGI;

html() if not caller;

sub html {

    print $cgi->header(-charset=>'UTF-8');
    print $cgi->start_html(-title=>'SEZ Asterisk', -style=>{'src'=>'./../style.css'});
    
    my $global_directory    = '/var/www/asterisk/records/';
    my $directory           = strftime "%Y/%m/%d", localtime;
    my $history             = $cgi->param('history');

    if ($history != 1) {
        if ( -d $global_directory . $directory){
            print "<p><a href=\"index.cgi?history=1\">История</a></p>";
            template_queue(); 
            print "<br>"; 
            record_table(
                dir     => $global_directory . $directory, 
                date    => "records/" . $directory
            );
        }
        
        else {
            $directory = '/var/www/asterisk/records' . strftime "/%Y", localtime;
            show_dir(date => $directory);
        }
    } else { 
        show_dir(
            date    => ($global_directory . strftime "/%Y", localtime), 
            history => 1
        );
    } 
}

sub record_table {
    my (%attr) = @_;
    opendir (DIR, $attr{dir});
    print "<table id='t01' border='1'><tr><th>Время</th><th>От кого звонок</th><th>Запись</th>";
        while (my $file = readdir(DIR)) {
            next if ($file =~ m/^\./);
            my @arr = split /-/, $file;
            print qq{
                <tr>
                    <td>$arr[0]</td>
                    <td>$arr[1]</td>
                    <td><audio controls><source src='../$attr{date}/$file' type='audio/mp3'></audio></td>
                </tr>
            };
        }
    print "<tr></table>";
    return 1;
}

sub show_dir {
    my (%attr) = @_;
    
    my $year    = strftime "/%Y", localtime;
    my $month   = $cgi->param('month');
    my $day     = $cgi->param('day');

    opendir (DIR, $attr{date});

    while (my $date = readdir(DIR)) {
        ($date eq '..') 
            ? $date = undef 
            : ($date eq '.') 
                ? $date = undef 
                : '';
        ($attr{history} = 1) 
            ? print "<p><a href=\"index.cgi?history=1&month=$date\">$date</a></p><hr></form>"
            : print "<p><a href=\"index.cgi?month=$date\">$date</a></p><hr></form>"
    }

    if ($month) {
        clean_list();
        opendir (DIR, "$attr{date}/$month");
        while (my $date = readdir(DIR)) {
            ($date eq '..' || $date eq '.') ? $date = undef : '';
            ($attr{history} = 1) 
                ? print "<p><a href=\"?history=1&month=$month&day=$date\">$date</a></p>"
                : print "<p><a href=\"?month=$month&day=$date\">$date</a></p>"
        }
    }

    if ($month && $day) {
        clean_list();
        record_table(dir => "$attr{date}/$month/$day", date => "records/$year/$month/$day")
    }
}

sub template_queue {
    print "<table border='1'><tr><th>Принято</th><th>Пропущено</th><tr>";
    print "<td>"; my $a = system qw(/etc/zabbix/asterisk-zabbix/run.py queue -f Calls -p queue_01);     print "</td>";
    print "<td>"; my $b = system qw(/etc/zabbix/asterisk-zabbix/run.py queue -f Abandoned -p queue_01); print "</td>";
    print "</tr></table>";
    return 1;
}

sub clean_list { return print "<script type=\'text/javascript\'>document.body.innerHTML = '';</script>"; }
