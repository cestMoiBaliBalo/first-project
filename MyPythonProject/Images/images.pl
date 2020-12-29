use strict;
use warnings;
use File::Basename;
use File::Find;
use Image::ExifTool ':Public';

# __author__ = 'Xavier ROSSET'
# __maintainer__ = 'Xavier ROSSET'
# __email__ = 'xavier.python.computing@protonmail.com'
# __status__ = "Development"


# ================
# Initializations.
# ================
my $i = 0;
my $level = 100;
my $root = "H:\\";
my $separator = "|";
my @images = ();
my @directories = ();
my @subdirectories;
my %map = ();
my $regex1;
my $regex2 = qr/\.jpg$/i;


# ================
# Local functions.
# ================
sub directories {
    if(not $map{"$File::Find::dir"}){
        if("$File::Find::dir" =~ /$regex1/g){
            $map{"$File::Find::dir"} = "$File::Find::dir";
            push(@subdirectories, $File::Find::dir);
        }
    }
}

sub files {
    if($_ =~ /$regex2/g) {
        my $file = $_;
        my $tagsref = ImageInfo($File::Find::name, "ExifIFD:DateTimeOriginal", "IPTC:CopyrightNotice");
        push(@images, [\$file, $tagsref]) if %$tagsref;
   }
}


# ===========
# Main logic.
# ===========
my $log = shift;
my $arguments = \@ARGV;
for(@$arguments){
    my $index = $i++;
    my $argument = "$arguments->[$index]";

    # Directory is fully qualified.
    push(@directories, "$argument") if(-d "$argument");

    # Directory is not fully qualified: look for sub-directories matching the pattern.
    if (not -d "$argument") {
        # no warnings;
        @subdirectories = ();
        $argument =~ s/\\/\\\\/g;
        $regex1 = qr/^$argument\d{2}$/;
        find({wanted => \&directories}, "$root");
        for(@subdirectories){
            push(@directories, $_) if(-d $_);
        }
    }
}

# Display walked folders.
if($log) {
    my $first = 1;
    for(sort @directories){
        $first = 0, print "Les répertoires traversés sont : ", "\n" if $first;
        print "$_", "\n";
    }
    print "\n" x 2;
}

# Store both image name and image original datetime into a plain text file.
find({wanted => \&files}, sort @directories);
if(scalar @images > 0){
    open(FH, ">:encoding(UTF-8)", "C:\\users\\Xavier\\Appdata\\Local\\Temp\\images.txt") or die $!;
    for(@images){
        my $line = ${$_->[0]} . $separator . $_->[1]->{DateTimeOriginal};
        $line = $line . $separator . $_->[1]->{CopyrightNotice} if $_->[1]->{CopyrightNotice};
        print FH $line, "\n";
    }
    $level = 0;
    close(FH);
}
exit "$level";
