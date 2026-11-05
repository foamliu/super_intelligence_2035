#!/usr/bin/env perl
use strict;
use warnings;

use File::Basename qw(basename dirname);
use File::Spec;

# ---------------------------------------------------------------------------
# check_connectFile_nets.pl
#
# Given a finesim control file (si.inp), this script:
#   1. locates every file reference whose basename starts with "connectFile"
#      (directly via .include/.inc in si.inp, or indirectly through the
#      .include/.inc hierarchy);
#   2. collects the ignored instance hierarchies from
#      `.option finesim_ignore = "..."` lines and from the sibling
#      `si.ignore_block` file (if present);
#   3. parses the referenced SPICE netlists to build the subckt/instance
#      hierarchy (.subckt ports, instance -> subckt mapping, top-level X);
#   4. for every `RConnect<...> <fullpathA> <fullpathB> <value>` line, splits
#      each fullpath into (instance path, net), then reports the net as
#      FOUND / MISSING / EXCLUDED.
#
# Usage: perl check_connectFile_nets.pl <si.inp>
# ---------------------------------------------------------------------------

my $si_inp = shift @ARGV;
if (!defined $si_inp) {
    print STDERR "Usage: perl check_connectFile_nets.pl <si.inp>\n";
    exit 2;
}

my $si_abs   = File::Spec->rel2abs($si_inp);
my $base_dir = dirname($si_abs);

# ---- generic helpers ------------------------------------------------------

# Remove an inline $ comment that is not inside a quoted string.
sub dep_comments {
    my ($s) = @_;
    my $out = '';
    my $in  = '';
    my $i   = 0;
    while ($i < length($s)) {
        my $c = substr($s, $i, 1);
        if ($in ne '') {
            $out .= $c;
            $in = '' if $c eq $in;
        } elsif ($c eq '"' || $c eq "'") {
            $in = $c;
            $out .= $c;
        } elsif ($c eq '$') {
            last;
        } else {
            $out .= $c;
        }
        $i++;
    }
    return $out;
}

# Read a file and return its logical lines ('+' continuations joined).
sub logical_lines {
    my ($file) = @_;
    open(my $fh, '<', $file) or return ();
    my @out;
    my $cur  = '';
    my $have = 0;
    while (my $l = <$fh>) {
        $l =~ s/\r?\n\z//;
        if ($l =~ /^\s*\+/) {
            $l =~ s/^\s*\+//;
            $cur .= ' ' . $l;
        } else {
            push @out, $cur if $have;
            $cur  = $l;
            $have = 1;
        }
    }
    push @out, $cur if $have;
    close $fh;
    return @out;
}

# Strip a trailing bus subscript, e.g. name[3], name<3>, name[3:0].
sub strip_bus {
    my ($n) = @_;
    $n =~ s/\s+\z//;
    $n =~ s/[\[<].*\z//;
    return $n;
}

# Extract the filename from the tail of a .include/.inc directive.
sub extract_filename {
    my ($s) = @_;
    $s =~ s/^\s+//;
    $s =~ s/\s+\z//;
    return '' if $s eq '';
    if ($s =~ /^(["'])(.*?)\1/s) {
        return $2;
    }
    my ($tok) = split(/\s+/, $s);
    return defined $tok ? $tok : '';
}

# Parse a string mixing quoted (space-separated) and unquoted tokens.
sub extract_quoted_tokens {
    my ($s) = @_;
    my @out;
    while ($s =~ /\G\s*(?:(["'])(.*?)\1|(\S+))/sg) {
        if (defined $2) {
            for my $t (split(/\s+/, $2)) {
                push @out, $t if $t ne '';
            }
        } else {
            push @out, $3 if defined $3 && $3 ne '';
        }
    }
    return @out;
}

# Resolve a referenced path: relative -> si.inp's directory.
sub resolve_ref {
    my ($ref) = @_;
    return $ref if $ref =~ m{^/};
    return "$base_dir/$ref";
}

# If a line is a .include/.inc directive, return its filename reference.
sub extract_include_ref {
    my ($line) = @_;
    my $c = dep_comments($line);
    $c =~ s/^\s+//;
    $c =~ s/\s+\z//;
    if ($c =~ /^\.\s*include\b\s*(.*)$/i) {
        return extract_filename($1);
    }
    if ($c =~ /^\.\s*inc\b\s*(.*)$/i) {
        return extract_filename($1);
    }
    return undef;
}

# ---- 1. discover connectFile* files and netlist files ---------------------

my %visited_file;
my @connectfiles;
my @net_files = ($si_abs);
my %net_file_seen = ($si_abs => 1);
my %conn_seen;

sub scan_refs {
    my ($file) = @_;
    return if $visited_file{$file}++;
    my @lines = logical_lines($file);
    return unless @lines;
    for my $l (@lines) {
        my $ref = extract_include_ref($l);
        next unless defined $ref;
        next if $ref eq '';
        my $path = resolve_ref($ref);
        my $b = basename($path);
        if ($b =~ /^connectFile/i) {
            unless ($conn_seen{$path}) {
                $conn_seen{$path} = 1;
                push @connectfiles, $path;
            }
        } else {
            unless ($net_file_seen{$path}) {
                $net_file_seen{$path} = 1;
                push @net_files, $path;
            }
            scan_refs($path);
        }
    }
}
scan_refs($si_abs);

# ---- 2. collect ignored instance hierarchies ------------------------------

my %ignore_seen;
my @ignore_paths;

# (a) .option finesim_ignore = "..." lines inside si.inp
for my $l (logical_lines($si_abs)) {
    my $c = dep_comments($l);
    # match the exact option name, not finesim_ignore_chkfunc_error etc.
    if ($c =~ /\bfinesim_ignore\b/i) {
        $c =~ s/^.*?\bfinesim_ignore\b//i;
        $c =~ s/^\s*=\s*//;
        for my $t (extract_quoted_tokens($c)) {
            if (!$ignore_seen{$t}) {
                $ignore_seen{$t} = 1;
                push @ignore_paths, $t;
            }
        }
    }
}

# (b) si.ignore_block file in the same directory (if present). Faithful
#     bundles rename it to si.ignore_block_SAME_SUFFIX (e.g. the "_A" of
#     "si.inp_A"), so derive the suffixed candidate from si.inp too.
{
    my $cb     = basename($si_abs);
    my $suffix = '';
    if ($cb =~ /^si\.inp(.*)$/) {
        $suffix = $1;
    }
    my %cand;
    $cand{"$base_dir/si.ignore_block"} = 1;
    $cand{"$base_dir/si.ignore_block$suffix"} = 1 if $suffix ne '';
    for my $cf (sort keys %cand) {
        next unless -f $cf;
        for my $l (logical_lines($cf)) {
            my $c = dep_comments($l);
            $c =~ s/^\s+//;
            $c =~ s/\s+\z//;
            next if $c eq '';
            next if $c =~ /^\*/;
            my ($tok) = split(/\s+/, $c);
            next unless defined $tok && $tok ne '';
            if (!$ignore_seen{$tok}) {
                $ignore_seen{$tok} = 1;
                push @ignore_paths, $tok;
            }
        }
    }
}

# ---- 3. build subckt / instance hierarchy from netlists -------------------

my @all_netlines;
for my $f (@net_files) {
    push @all_netlines, logical_lines($f);
}

# first pass: all subckt names
my %subckt_names;
for my $l (@all_netlines) {
    my $c = dep_comments($l);
    if ($c =~ /^\.\s*subckt\s+(\S+)/i) {
        $subckt_names{$1} = 1;
    }
}

# second pass: ports + instances
my %ports;      # subckt -> { port => 1 } (raw + bus-stripped keys)
my %sub_insts;  # parent subckt -> { inst => subckt type }
my %top_insts;  # inst -> subckt type
my @stack;

for my $l (@all_netlines) {
    my $c = dep_comments($l);
    $c =~ s/^\s+//;
    $c =~ s/\s+\z//;
    next if $c eq '';

    if ($c =~ /^\.\s*subckt\s+(\S+)\s*(.*)$/i) {
        my ($name, $ps) = ($1, $2);
        push @stack, $name;
        my %ph;
        for my $p (split(/\s+/, $ps)) {
            next if $p eq '';
            $ph{$p} = 1;
            $ph{strip_bus($p)} = 1;
        }
        $ports{$name} = \%ph;
    }
    elsif ($c =~ /^\.\s*ends\b/i) {
        pop @stack;
    }
    elsif ($c =~ /^X\S/) {
        my @tok = split(/\s+/, $c);
        my $inst = $tok[0];
        # instance type = last token naming a known subckt; fallback to the
        # last token that does not look like a param=value pair.
        my $type;
        for (my $i = $#tok; $i >= 1; $i--) {
            if ($subckt_names{$tok[$i]}) {
                $type = $tok[$i];
                last;
            }
        }
        if (!defined $type) {
            for (my $i = $#tok; $i >= 1; $i--) {
                if ($tok[$i] !~ /=/) {
                    $type = $tok[$i];
                    last;
                }
            }
        }
        next unless defined $type;
        if (@stack) {
            $sub_insts{$stack[-1]}{$inst} = $type;
        } else {
            $top_insts{$inst} = $type;
        }
    }
}

# ---- 4. resolution helpers -------------------------------------------------

sub leaf_type {
    my ($path) = @_;
    my @tok = split(/\./, $path);
    return undef unless @tok;
    my $type = $top_insts{$tok[0]};
    return undef unless defined $type;
    for (my $i = 1; $i <= $#tok; $i++) {
        my $inst = $tok[$i];
        return undef
          unless exists $sub_insts{$type} && exists $sub_insts{$type}{$inst};
        $type = $sub_insts{$type}{$inst};
    }
    return $type;
}

sub is_excluded {
    my ($path) = @_;
    for my $ig (@ignore_paths) {
        return 1 if $path eq $ig;
        return 1 if index($path, "$ig.") == 0;
    }
    return 0;
}

sub net_exists {
    my ($type, $net) = @_;
    return 0 unless defined $type;
    my $ph = $ports{$type};
    return 0 unless defined $ph;
    return 1 if exists $ph->{$net};
    return 1 if exists $ph->{strip_bus($net)};
    return 0;
}

# ---- 5. verify every RConnect net -----------------------------------------

my ($total, $found, $missing, $excluded) = (0, 0, 0, 0);

for my $cf (@connectfiles) {
    for my $l (logical_lines($cf)) {
        my $c = dep_comments($l);
        $c =~ s/^\s+//;
        $c =~ s/\s+\z//;
        next if $c eq '';
        next if $c =~ /^\*/;
        my @tok = split(/\s+/, $c);
        next if @tok < 3;
        next unless $tok[0] =~ /^RConnect/i;

        for my $fp ($tok[1], $tok[2]) {
            my @parts = split(/\./, $fp);
            my $net   = pop @parts;
            my $path  = join('.', @parts);

            my $status;
            if (is_excluded($path)) {
                $status = 'EXCLUDED';
                $excluded++;
            } else {
                my $lt = leaf_type($path);
                if (net_exists($lt, $net)) {
                    $status = 'FOUND';
                    $found++;
                } else {
                    $status = 'MISSING';
                    $missing++;
                }
            }
            $total++;
            print "RESULT net=$net path=$path status=$status\n";
        }
    }
}

print "SUMMARY total=$total found=$found missing=$missing excluded=$excluded\n";