#!/bin/bash
ffmpeg="$HOME/ffmpeg/bin/ffmpeg"
music="/storage/emulated/0/Music/muzyka"
target="m4a"

for file in "$music"/*.webm; do
    if [[ -f "$file" ]]; then
        base="${file%.*}"
        "$ffmpeg" -i "$file" "${base}.$target"
        echo "$file processed"
````````rm -f "$file"
    fi
done
echo "done"
