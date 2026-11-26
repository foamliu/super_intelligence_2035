NR==FNR { excl[$0]=1; next }
FNR==1 { next }
{
  mc = $5+0
  if (mc < 10) next
  sid = $4
  sub(/\.messages\.json$/, "", sid)
  sub(/\.json$/, "", sid)
  sub(/\.messages\.archive$/, "", sid)
  if (sid in excl) next
  if ($0 in excl) next
  if ($6 !~ /waveview|cosmos|skill|netlist|spiros|spectrum|analog|schematic/) next
  print mc "\t" $4 "\t" $3 "\t" $2 "\t" $6 "\t" $1
}
