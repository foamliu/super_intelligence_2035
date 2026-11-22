BEGIN{FS="\t"; OFS="\t"}
NR==FNR { touched[$1]=1; next }
{
  sf=$4; sub(/\.messages\.json$/, "", sf); sub(/\.json$/, "", sf);
  mc=$5+0; kw=$6;
  if (mc<5) next;
  if (touched[sf]) next;
  if (kw !~ /hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim/) next;
  print mc"\t"$4"\t"$3"\t"$2"\t"kw
}
