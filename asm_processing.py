import re

def extract_main_loop_region(text: str) -> str:
    """
    Tek bir .asm dosyasının içinden '; Main loop here' ile
    '; Stack Pointer definition' arasını alır.
    """
    lines = text.splitlines()
    main_started = False
    result = []

    for line in lines:
        if not main_started and '; Main loop here' in line:
            main_started = True
            continue

        if main_started:
            if '; Stack Pointer definition' in line:
                break
            result.append(line)

    return '\n'.join(result)


def normalize_asm(text: str):
    """
    Main loop bölgesini normalize eder:
    - Yorumları siler
    - Label'ları #BLOCK_START ile işaretler
    - Register'ları R yapar
    - Sayıları IMM yapar
    """
    lines = []
    for raw in text.splitlines():
        # Yorumları sil
        line = raw.split(';', 1)[0]
        line = line.strip()
        if not line:
            continue

        # Label + opsiyonel komut (inner:, outer: gibi)
        m = re.match(r'^([A-Za-z_.$][\w.$]*)\s*:(.*)$', line)
        if m:
            # Blok başlangıcı işareti
            lines.append('#BLOCK_START')
            rest = m.group(2).strip()
            if not rest:
                continue
            line = rest

        # Büyük harfe çevir
        line = line.upper()

        # R0..R15 -> R (sadece tam tokenlar)
        line = re.sub(r'\bR(1[0-5]|[0-9])\b', 'R', line)

        # Sayılar -> IMM (16, #10, 0AH, #0AH, 0x1F vs.)
        line = re.sub(
            r'\b#?-?(0X[0-9A-F]+|[0-9]+|[0-9A-F]+H)\b',
            'IMM',
            line
        )

        # Fazla boşlukları toparla
        line = re.sub(r'\s+', ' ', line)

        if line:
            lines.append(line)

    return lines
