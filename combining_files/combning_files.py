def parse_tamil_kurals(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    kurals = []
    for line in lines:
        parts = line.strip().split('$')
        if len(parts) == 2:
            kurals.append((parts[0].strip(), parts[1].strip()))
    return kurals

def parse_english_meanings(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    english_data = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line and line[0].isdigit() and '.' in line:
            poetic = lines[i + 1].strip()
            poetic2 = lines[i + 2].strip()
            literal = lines[i + 4].strip() if i + 4 < len(lines) else ''
            english_data.append((poetic + ' ' + poetic2, literal))
            i += 5
        else:
            i += 1
    return english_data

def combine_and_save(tamil_file, english_file, output_file):
    tamil_kurals = parse_tamil_kurals(tamil_file)
    english_kurals = parse_english_meanings(english_file)

    with open(output_file, 'w', encoding='utf-8') as f:
        for i, ((t1, t2), (etrans, emean)) in enumerate(zip(tamil_kurals, english_kurals), start=1):
            f.write(f"Kural {i}:\n")
            f.write("Tamil:\n")
            f.write(f"{t1}\n{t2}\n\n")
            f.write("Poetic Translation:\n")
            f.write(f"{etrans}\n\n")
            f.write("Literal Meaning:\n")
            f.write(f"{emean}\n\n")
            f.write("="*40 + "\n\n")

# Example usage:
combine_and_save('1330_thirukuralgal.txt', 'thirukural_english_translation.txt', 'combined_output.txt')

