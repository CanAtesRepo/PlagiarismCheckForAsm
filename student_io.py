import os
from asm_processing import extract_main_loop_region, normalize_asm
from plagiarism_core import compare_normalized


def load_all_students(root_dir: str):
    """
    root_dir altındaki her klasörü bir öğrenci kabul eder.
    Her klasördeki ilk .asm dosyasını bulur, okur, normalize eder.

    Dönüş:
        {
          "ogrenci_adi": {
               "path": ".../ogrenci_adi/dosya.asm",
               "norm": [... normalize satırlar ...]
          },
          ...
        }
    """
    students = {}

    for entry in os.listdir(root_dir):
        student_dir = os.path.join(root_dir, entry)
        if not os.path.isdir(student_dir):
            continue  # sadece klasörler öğrenci sayılır

        student_name = entry  # klasör adı = öğrenci adı

        # Klasördeki ilk .asm dosyasını bul
        asm_file_path = None
        for f in os.listdir(student_dir):
            if f.lower().endswith(".asm"):
                asm_file_path = os.path.join(student_dir, f)
                break

        if asm_file_path is None:
            print(f"[UYARI] '{student_name}' klasöründe .asm dosyası bulunamadı, atlanıyor.")
            continue

        with open(asm_file_path, "r", encoding="utf-8", errors="ignore") as f:
            asm_text = f.read()

        main_region = extract_main_loop_region(asm_text)
        norm = normalize_asm(main_region)

        students[student_name] = {
            "path": asm_file_path,
            "norm": norm,
        }

    return students


def compute_pairwise_similarities(students: dict, threshold_percent: float, k=3):
    """
    Her öğrenciyi diğer tüm öğrencilerle karşılaştırır.
    Sadece threshold'u geçen benzerlikleri döner.

    Dönüş:
        {
          "ogrenci1": [("ogrenci2", 85.3), ("ogrenci5", 91.2)],
          "ogrenci2": [("ogrenci1", 85.3)],
          ...
        }
    """
    names = sorted(students.keys())
    results = {name: [] for name in names}

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            s1 = names[i]
            s2 = names[j]

            norm1 = students[s1]["norm"]
            norm2 = students[s2]["norm"]

            scores = compare_normalized(norm1, norm2, k=k)

            # Logic benzerlik için: opcode n-gram Jaccard
            sim_percent = scores["opcode_ngram_jaccard"] * 100.0

            # Eşik üstü ise kaydet
            if sim_percent >= threshold_percent:
                results[s1].append((s2, sim_percent))
                results[s2].append((s1, sim_percent))

    return results


def save_results(results: dict, output_path: str, threshold_percent: float):
    """
    Sonuç sözlüğünü tek bir text dosyasına yazar.

    - Her çift (A,B) sadece bir kere raporlanır (A→B ve B→A tekrar etmez).
    - Özet bölümünde her öğrencinin KAÇ kişiyle eşik üstü benzerliği olduğu gösterilir.
    """
    # Özet için: her öğrencinin kaç kişiyle benzerliği var?
    match_counts = {student: len(similars) for student, similars in results.items()}

    # Çiftlerin tekrar yazılmaması için
    seen_pairs = set()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Plagiarism results (threshold = {threshold_percent:.1f}%)\n")
        f.write("=====================================================\n\n")

        # ───────────────────────────────────────────────
        # 1) Summary: kaç eşleşmesi var?
        # ───────────────────────────────────────────────
        f.write("Summary: number of matches per student (above threshold)\n")
        f.write("--------------------------------------------------------\n")

        any_flagged = False
        for student in sorted(results.keys()):
            count = match_counts[student]
            if count > 0:
                any_flagged = True
                f.write(f"{student}: {count} match(es)\n")

        if not any_flagged:
            f.write("\nNo pairs above the threshold were found.\n")
            return

        f.write("\n\n")

        # ───────────────────────────────────────────────
        # 2) Detailed pairs (her çift tek sefer)
        # ───────────────────────────────────────────────
        f.write("Detailed similar pairs (each pair listed only once)\n")
        f.write("--------------------------------------------------------\n\n")

        for student in sorted(results.keys()):
            new_similars = []
            for other, sim in results[student]:

                pair_key = tuple(sorted((student, other)))
                if pair_key in seen_pairs:
                    continue

                seen_pairs.add(pair_key)
                new_similars.append((other, sim))

            if not new_similars:
                continue

            f.write(f"Student: {student}\n")
            for other, sim in sorted(new_similars, key=lambda x: -x[1]):
                f.write(f"  -> Similar to: {other}   ({sim:.1f}%)\n")
            f.write("\n")

    print(f"Sonuç dosyası kaydedildi: {output_path}")
