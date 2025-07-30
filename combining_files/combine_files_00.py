# Combine file1.txt and file2.txt into combined.txt
with open('combined.txt', 'w') as outfile:
    for fname in ['30_thirukuralgal.txt', '30_thirukural_translation.txt']:
        with open(fname) as infile:
            outfile.write(infile.read())
            outfile.write('\n')  # Optional: add a newline between files
