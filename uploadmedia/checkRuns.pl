##!/usr/bin/perl -w
 
@files = <*>;
my $DIR = '/tmp/upload_cache';
my %images;
my %jobs;
my %missing;
foreach my $filename ( <$DIR/*.csv>) {
   open FH,"<$filename";
   $i = 0;
   $filename =~ s/$DIR\///;
   $filename =~ s/.csv$//;
   while (<FH>) {
     next if /^name/; # skip header rows
     $i++;
     chomp;
     ($name,$size,$objectnumber,$date,$creator,$contributor,$rightsholder) = split /[\t\|]/;
     my ($run,$step) = $filename =~ /^(.*?)\.(.*?)$/;
     #next if $step =~ /step1/;
     #$images{$filename}++;
     #print "$run\t$step\t$i\t\n";
     $jobs{$run}{$step}++;
     $images{$name}{$run}{$step}++;
     if ($ARGV[0] eq 'missing') {
       $missing{$name} = $_;
     }
   }
}

if ($ARGV[0] eq 'jobs') {

  @columnheaders = split(' ','step1 original step2 step3 processed inprogress');
  print "job\t";
  print join "\t",@columnheaders;
  print "\tdiscrepancy";
  print "\n";
  foreach my $job (sort keys %jobs) {
    print $job."\t";
    my %steps = %{$jobs{$job}};
    foreach my $step (@columnheaders) {
    #print $step."\t";
      print $steps{$step} . "\t";
    }
    $discrepancy = $steps{'original'} - $steps{'processed'};
    print $discrepancy if $discrepancy > 0 ;
    print "\n";
  }
}

elsif  ($ARGV[0] eq 'missing') { 
  foreach my $name (sort keys %images) {
    my $isMissing = 1;
    my %runs = %{$images{$name}};
    foreach my $run (sort keys %runs) { 
      #print $run."\t";
      my %steps = %{$runs{$run}};
      foreach my $step (sort keys %steps) { 
	#print $step."\t";
	$isMissing = 0 if $step =~ /(processed|step1|inprogress)/;
      }
    }
  print "$missing{$name}\n" if $isMissing;
  }
}

else {
  foreach my $name (sort keys %images) {
    print $name."\t";
    my %runs = %{$images{$name}};
    foreach my $run (sort keys %runs) { 
      print $run."\t";
      my %steps = %{$runs{$run}};
      foreach my $step (sort keys %steps) { 
	print $step."\t";
      }
    }
  print "\n";
  }
}
  
