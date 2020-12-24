use warnings;
use strict;
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
my $arguments = \@ARGV;
my $i = 0;
my $level = 100;
my $root = "H:\\";
my @images = ();
my @directories = ();
my @subdirectories;
my %map = ();
my $regex1;
my $regex2 = qr/\.[^.]+$/;


# ================
# Local functions.
# ================
sub directories {
    if(not $map{"$File::Find::dir"}){
        if("$File::Find::dir" =~ $regex1){
            $map{"$File::Find::dir"} = "$File::Find::dir";
            push(@subdirectories, $File::Find::dir);
        }
    }
}


sub files {
    my($filename, $path, $suffix) = fileparse($_, ($regex2));
    if(length("$suffix") > 1){
        my $ext = substr("$suffix", 1);
        if(lc("$ext") eq "jpg") {
            my $tagsref = ImageInfo($File::Find::name, "ExifIFD:DateTimeOriginal", "IPTC:CopyrightNotice");
            my $file = $_;
            push(@images, [\$file, $tagsref]) if %$tagsref;
       }
    }
}


# ===========
# Main logic.
# ===========
for(@$arguments){
    my $index = $i++;
    my $argument = "$arguments->[$index]";

    # Directory is fully qualified.
    push(@directories, "$argument") if(-d "$argument");

    # Directory is not fully qualified: look for sub-directories matching the pattern.
    if (not -d "$argument") {
        no warnings;
        @subdirectories = ();
        $argument =~ s/\\/\\\\/g;
        $regex1 = qr/^$argument\d{2}$/;
        # print "$regex1" . "\n";
        find({wanted => \&directories}, "$root");
        for(@subdirectories){
            push(@directories, $_) if(-d $_);
        }
    }

}

# Display walked folders.
# my $first = 1;
# for(sort @directories){
#     if($first) {
#         $first = 0;
#         print "Les répertoires traversés sont : " . "\n";
#     }
#     print "$_" . "\n";
# }
# print "\n" x 2;

# Store both image name and image original datetime into a plain text file.
find({wanted => \&files}, sort @directories);
if(scalar @images > 0){
    open(FH, ">:encoding(UTF-8)", "C:\\users\\Xavier\\Appdata\\Local\\Temp\\images.txt") or die $!;
    for(@images){
        my $fileref = $_->[0];
        my $tagsref = $_->[1];
        print "$$fileref" . "\n";
        print $tagsref->{DateTimeOriginal} . "\n";
        print $tagsref->{CopyrightNotice} . "\n" if $tagsref->{CopyrightNotice};
        # my $line = "$image->[0]" . "|" . "$values->[0]";
        # print FH "$line" . "\n";
    }
    $level = 0;
    close(FH);
}
exit "$level";
