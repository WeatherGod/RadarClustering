#! /usr/bin/perl -w

use strict;
use Getopt::Long;
$Getopt::Long::ignorecase = 0;	# make options case sensitive

my ($runName, $inputFile,
    $upperStart, $upperCnt, $upperEnd,
    $lowerStart, $lowerCnt, $lowerEnd,
    $paddingStart, $paddingCnt, $paddingEnd,
    $reachStart, $reachCnt, $reachEnd,
    $subClustStart, $subClustEnd) 	= (undef, undef, 1.96, 1, 1.96,
							-0.25, 1, -0.25,
							5, 1, 5,
							2.5, 1, 2.5,
							0, 0);

if (!GetOptions(
	"help|h"	=> sub { PrintHelp();
				 exit(1); },
	"syntax|x"	=> sub { PrintSyntax();
				 exit(2); },
	"runname|r=s"	=> \$runName,
	"input|i=s"	=> \$inputFile,

	"us=f"		=> \$upperStart,
	"uc=i"		=> \$upperCnt,
	"ue=f"		=> \$upperEnd,

	"ls=f"		=> \$lowerStart,
	"lc=i"		=> \$lowerCnt,
	"le=f"		=> \$lowerEnd,

	"ps=f"		=> \$paddingStart,
	"pc=i"		=> \$paddingCnt,
	"pe=f"		=> \$paddingEnd,

	"rs=f"		=> \$reachStart,
	"rc=i"		=> \$reachCnt,
	"re=f"		=> \$reachEnd,

	"ss=i"		=> \$subClustStart,
	"se=i"		=> \$subClustEnd) )
{
	PrintSyntax();
	exit(2);
}


if (!defined($runName))
{
	print STDERR "ERROR: Missing Runname!\n";
	PrintSyntax();
	exit(2);
}

if (!defined($inputFile))
{
	print STDERR "ERROR: Missing input filename!\n";
	PrintSyntax();
	exit(2);
}

if ($upperCnt <= 0 || $lowerCnt <= 0 || $paddingCnt <= 0 || $reachCnt <= 0)
{
	print STDERR "ERROR: The parameter counts must be greater than zero!\n";
	exit(2);
}


my $upperIncrem = ($upperCnt > 1) ? ($upperEnd - $upperStart) / ($upperCnt - 1) : 0.0;
my $lowerIncrem = ($lowerCnt > 1) ? ($lowerEnd - $lowerStart) / ($lowerCnt - 1) : 0.0;
my $paddingIncrem = ($paddingCnt > 1) ? ($paddingEnd - $paddingStart) / ($paddingCnt - 1) : 0.0;
my $reachIncrem = ($reachCnt > 1) ? ($reachEnd - $reachStart) / ($reachCnt - 1) : 0.0;


NewRun($runName);

unlink("logfile.txt");

for (my $upperIndex = 0; $upperIndex < $upperCnt; $upperIndex++)
{
	my $upperLevel = $upperStart + ($upperIndex * $upperIncrem);

	for (my $lowerIndex = 0; $lowerIndex < $lowerCnt; $lowerIndex++)
	{
		my $lowerLevel = $lowerStart + ($lowerIndex * $lowerIncrem);

		for (my $paddingIndex = 0; $paddingIndex < $paddingCnt; $paddingIndex++)
		{
			my $paddingLevel = $paddingStart + ($paddingIndex * $paddingIncrem);

			for (my $reachIndex = 0; $reachIndex < $reachCnt; $reachIndex++)
			{
				my $reachLevel = $reachStart + ($reachIndex * $reachIncrem);

				foreach my $subClustDepth ($subClustStart ... $subClustEnd)
				{
					if ($inputFile =~ /^(.*\/?)data\/.*\/(.*)\.nc$/)
					{
						my $outName = sprintf("%sclustInfo/%s/%s_u%.2f_l%.2f_p%.2f_r%.2f_s%d.nc",
								      $1, $runName, $2, $upperLevel, $lowerLevel, $paddingLevel, 
								      $reachLevel, $subClustDepth);
						DoCluster($inputFile, $outName, $upperLevel, $lowerLevel, $paddingLevel, $reachLevel, $subClustDepth);
					}
					else
					{
						print STDERR "ERROR: Problem with doing regex on the input file name: $inputFile\n";
						print STDERR "Skipping...\n";
					}
				}
			}
		}
	}
}


exit(0);




########################## Functions ###########################
sub PrintHelp
{
	PrintSyntax();

	print STDERR "This program will execute the clustering program repeatedly on the same file\n";
	print STDERR "with slightly varying parameters.\n\n";
}

sub PrintSyntax
{
	print STDERR "\nparamrun.pl --runname|-r _RUNNAME_ --input|-i _INPUTFILE_\n";
	print STDERR "            [--us _UPPERSTART_] [--uc _UPPERCNT_] [--ue _UPPEREND_}\n";
	print STDERR "            [--ls _LOWERSTART_] [--lc _LOWERCNT_] [--le _LOWEREND_}\n";
	print STDERR "            [--ps _PADSTART_] [--pc _PADCNT_] [--pe _PADEND_}\n";
	print STDERR "            [--rs _REACHSTART_] [--rc _REACHCNT_] [--re _REACHEND_}\n";
	print STDERR "            [--ss _SUBCLUSTSTART_] [--se _SUBCLUSTEND_]\n";
	print STDERR "            [--syntax | -x] [--help | -h]\n\n";
}

sub NewRun
{
	mkdir("clustInfo/$_[0]");
	mkdir("PPI/$_[0]");
	mkdir("ClustHisto/$_[0]");
}

sub DoCluster
{
	my ($inputFile, $outputFile, $upper, $lower, $padding, $reach, $subClustDepth) = @_;

	if (system("./test_radar -i '$inputFile' -o '$outputFile' -u $upper -l $lower -p $padding -r $reach -s $subClustDepth >> logfile.txt") != 0)
	{
		print STDERR "ERROR: Problem with running 'test_radar'!\n";
		exit(3);
	}
}

