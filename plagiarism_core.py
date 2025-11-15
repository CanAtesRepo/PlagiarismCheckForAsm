import difflib

def extract_opcodes(norm_lines):
    """
    normalize_asm çıktısından opcode dizisi üretir.
    #BLOCK_START ve assembler directive'leri (.DATA, .TEXT, .WORD) atar.
    """
    opcodes = []
    for line in norm_lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#BLOCK_START'):
            continue
        if line.startswith('.'):
            continue

        parts = line.split()
        if not parts:
            continue

        mnemonic = parts[0].split('.')[0]  # "ADD.W" -> "ADD"
        opcodes.append(mnemonic)

    return opcodes


def make_ngrams(seq, k=3):
    if len(seq) < k:
        return set()
    return {tuple(seq[i:i + k]) for i in range(len(seq) - k + 1)}


def jaccard_similarity(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union


def compare_normalized(norm1, norm2, k=3):
    """
    İki normalize edilmiş kod listesi için farklı benzerlik skorları döner.
    Threshold için -> opcode_n_gram_jaccard.
    """
    # 1) Satır bazlı benzerlik
    line_sim = difflib.SequenceMatcher(None, norm1, norm2).ratio()

    # 2) Opcode dizileri
    ops1 = extract_opcodes(norm1)
    ops2 = extract_opcodes(norm2)

    opcode_seq_sim = difflib.SequenceMatcher(None, ops1, ops2).ratio()

    # 3) Opcode n-gram Jaccard (logic pattern)
    ngrams1 = make_ngrams(ops1, k=k)
    ngrams2 = make_ngrams(ops2, k=k)
    opcode_ngram_jacc = jaccard_similarity(ngrams1, ngrams2)

    return {
        "line_similarity": line_sim,
        "opcode_sequence_similarity": opcode_seq_sim,
        "opcode_ngram_jaccard": opcode_ngram_jacc,
    }
