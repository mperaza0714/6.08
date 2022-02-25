#!/usr/bin/env bash

script_dir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
base_dir="$(dirname $script_dir)"
out_file="$base_dir/docs/code.md"

cat > $out_file <<EOF
## Code Appendix

EOF

shopt -s nullglob
#
# CHANGE DIRECTORIES AND EXTENSIONS HERE
#
for file in $base_dir/{,html/}*.{py,html}; do
    base="$(basename $file)"
    printf "\`$base\`:\n\n\`\`\`\n" >> $out_file
    cat $file >> $out_file
    printf "\n\`\`\`\n\n" >> $out_file
done
