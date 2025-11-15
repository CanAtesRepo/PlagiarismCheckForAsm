from student_io import load_all_students, compute_pairwise_similarities, save_results
import os

# Bütün öğrenci klasörlerinin bulunduğu klasör
# Ör: "C:/projeler/odev1/submissions"
ROOT_DIR = "./submissions"

# Yüzde cinsinden eşik (80 => %80 ve üzeri benzerlikleri raporla)
THRESHOLD_PERCENT =80.0

# Opcode n-gram uzunluğu (logic pattern için)
NGRAM_K = 3

# Sonuçların yazılacağı klasör ve dosya
RESULT_DIR = "./results"
RESULT_FILE = os.path.join(RESULT_DIR, "plagiarism_results.txt")


def main():
    print(f"Kök klasör: {ROOT_DIR}")
    print(f"Eşik (threshold): %{THRESHOLD_PERCENT:.1f}")

    # results klasörünü oluştur (yoksa)
    os.makedirs(RESULT_DIR, exist_ok=True)

    # Öğrencileri yükle
    students = load_all_students(ROOT_DIR)
    print(f"Bulunan öğrenci sayısı: {len(students)}")

    if len(students) < 2:
        print("Karşılaştırma yapmak için en az 2 öğrenci gerekli.")
        return

    # Pairwise benzerlikleri hesapla
    results = compute_pairwise_similarities(
        students,
        threshold_percent=THRESHOLD_PERCENT,
        k=NGRAM_K,
    )

    # Sonuçları dosyaya yaz
    save_results(results, RESULT_FILE, THRESHOLD_PERCENT)


if __name__ == "__main__":
    main()
