from difflib import HtmlDiff
import html


def generate_html_report(students: dict, results: dict, output_path: str, threshold_percent: float, ngram_k: int = 3):
    """
    Öğrenci benzerlik sonuçlarına göre tek bir HTML raporu üretir.

    - Solda öğrenci seçimi (dropdown).
    - Seçilen öğrenci için benzer bulunduğu diğer öğrenciler ve yüzdeleri listelenir.
    - Bir çifte tıklayınca, aşağıda yan yana diff (normalize edilmiş kod) gösterilir.
    """

    # 1) Öğrenci listesi
    all_student_names = sorted(results.keys())

    # Her öğrenci için: other -> max(similarity)
    cleaned_matches = {name: {} for name in all_student_names}
    for student in all_student_names:
        for other, sim in results[student]:
            if other not in cleaned_matches[student] or sim > cleaned_matches[student][other]:
                cleaned_matches[student][other] = sim

    # En az bir match'i olan öğrenciler
    matched_students = [s for s in all_student_names if cleaned_matches[s]]

    # Eğer kimsenin match'i yoksa yine de boş bir rapor üretelim
    # (dropdown boş olur, mesaj yazar)
    # 2) Diff tabloları: her (A,B) çifti için bir tane
    diff_maker = HtmlDiff(wrapcolumn=80)
    pair_diffs_html = {}  # key: "A||B"

    for student in matched_students:
        for other, sim in cleaned_matches[student].items():
            if student == other:
                continue
            a, b = sorted((student, other))
            pair_key = f"{a}||{b}"
            if pair_key in pair_diffs_html:
                continue

            norm1 = students[a]["norm"]
            norm2 = students[b]["norm"]

            table_html = diff_maker.make_table(
                norm1,
                norm2,
                fromdesc=a,
                todesc=b,
                context=True,
                numlines=2
            )
            pair_diffs_html[pair_key] = table_html

    # 3) JS için matchesData: yalnızca matched_students
    def js_escape(s: str) -> str:
        return s.replace("\\", "\\\\").replace("'", "\\'")

    matches_js_lines = []
    matches_js_lines.append("{")
    first_student = True
    for student in matched_students:
        if not first_student:
            matches_js_lines.append(",")
        first_student = False
        matches_js_lines.append(f"  '{js_escape(student)}': [")
        first = True
        for other, sim in sorted(cleaned_matches[student].items(), key=lambda x: -x[1]):
            if not first:
                matches_js_lines.append(",")
            first = False
            matches_js_lines.append(
                f"    {{other: '{js_escape(other)}', sim: {sim:.1f}}}"
            )
        matches_js_lines.append("  ]")
    matches_js_lines.append("}")
    matches_js_obj = "\n".join(matches_js_lines)

    # 4) Gizli diff div'lerini üret
    diff_divs = []
    for pair_key, table_html in pair_diffs_html.items():
        a, b = pair_key.split("||")
        div_id = f"diff-{a}--{b}"
        diff_divs.append(f'<div id="{html.escape(div_id)}" class="diff-pair" style="display:none;">')
        diff_divs.append(table_html)
        diff_divs.append("</div>")
    diff_divs_html = "\n".join(diff_divs)

    # 5) Dropdown seçenekleri (sadece match'i olanlar)
    options_html = "\n".join(
        f'                <option value="{html.escape(name)}">{html.escape(name)}</option>'
        for name in matched_students
    )

    # 6) Ana HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MSP430 Plagiarism Report</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            background: #f5f7fb;
            color: #222;
        }}
        header {{
            background: #1f3b8f;
            color: white;
            padding: 16px 24px;
        }}
        header h1 {{
            margin: 0;
            font-size: 22px;
        }}
        header p {{
            margin: 4px 0 0 0;
            font-size: 13px;
            opacity: 0.9;
        }}
        .container {{
            display: flex;
            gap: 16px;
            padding: 16px 24px 24px 24px;
        }}
        .panel {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            padding: 16px;
        }}
        .panel-left {{
            width: 260px;
            flex-shrink: 0;
        }}
        .panel-right {{
            flex: 1;
            min-width: 0;
        }}
        label {{
            display: block;
            font-size: 13px;
            margin-bottom: 6px;
            font-weight: 600;
        }}
        select {{
            width: 100%;
            padding: 6px 8px;
            border-radius: 6px;
            border: 1px solid #ccd3e3;
            font-size: 13px;
        }}
        table.matches {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-top: 8px;
        }}
        table.matches th, table.matches td {{
            padding: 6px 8px;
            border-bottom: 1px solid #eef0f6;
        }}
        table.matches th {{
            text-align: left;
            background: #f3f5fb;
            font-weight: 600;
        }}
        table.matches tr:hover td {{
            background: #f8faff;
        }}
        .btn-view {{
            border: none;
            background: #1f3b8f;
            color: white;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
            cursor: pointer;
        }}
        .btn-view:hover {{
            background: #324ea3;
        }}
        .summary-line {{
            font-size: 13px;
            margin-top: 8px;
            color: #555;
        }}
        .no-matches {{
            font-size: 13px;
            color: #888;
            margin-top: 10px;
        }}
        table.diff {{
            font-family: "Fira Code", "Consolas", "Courier New", monospace;
            font-size: 12px;
            border: 1px solid #ccd3e3;
            margin-top: 12px;
        }}
        .diff_header {{
            background-color: #e4e8f5;
            font-weight: bold;
        }}
        .diff_next {{
            background-color: #f5f7fb;
        }}
        .diff_add {{
            background-color: #d7ffd7;
        }}
        .diff_chg {{
            background-color: #fff3b0;
        }}
        .diff_sub {{
            background-color: #ffd6d6;
        }}
        .diff-pair-title {{
            font-size: 14px;
            font-weight: 600;
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <header>
        <h1>MSP430 Assembly Plagiarism Report</h1>
        <p>Threshold: {threshold_percent:.1f}% &middot; Opcode n-gram (k={ngram_k}) based similarity</p>
    </header>
    <div class="container">
        <div class="panel panel-left">
            <label for="studentSelect">Select student</label>
            <select id="studentSelect">
                <option value="">-- choose --</option>
{options_html}
            </select>
            <p class="summary-line" id="summaryLine"></p>
        </div>
        <div class="panel panel-right">
            <h3 style="margin-top:0;">Matches</h3>
            <div id="matchesContainer">
                <p class="no-matches">Select a student to see matches.</p>
            </div>
            <div id="diffContainer" style="margin-top:16px;">
            </div>
        </div>
    </div>
    <!-- Gizli diff tabloları -->
    <div style="display:none;">
{diff_divs_html}
    </div>
    <script>
        const matchesData = {matches_js_obj};
        const studentSelect = document.getElementById('studentSelect');
        const matchesContainer = document.getElementById('matchesContainer');
        const diffContainer = document.getElementById('diffContainer');
        const summaryLine = document.getElementById('summaryLine');

        function clearDiff() {{
            diffContainer.innerHTML = '';
        }}

        function showMatchesForStudent(student) {{
            clearDiff();

            if (!student || !matchesData[student]) {{
                matchesContainer.innerHTML = '<p class="no-matches">Select a student to see matches.</p>';
                summaryLine.textContent = '';
                return;
            }}

            const matches = matchesData[student];
            if (matches.length === 0) {{
                matchesContainer.innerHTML = '<p class="no-matches">No matches above threshold for this student.</p>';
                summaryLine.textContent = 'This student has 0 match(es) above threshold.';
                return;
            }}

            summaryLine.textContent = 'This student has ' + matches.length + ' match(es) above threshold.';

            let htmlTable = ''
                + '<table class="matches">'
                + '<thead><tr>'
                + '<th>Other student</th>'
                + '<th>Similarity (%)</th>'
                + '<th>Action</th>'
                + '</tr></thead><tbody>';

            for (let i = 0; i < matches.length; i++) {{
                const m = matches[i];
                const other = m.other;
                const sim = m.sim.toFixed(1);
                const a = (student < other) ? student : other;
                const b = (student < other) ? other : student;
                const pairId = 'diff-' + a + '--' + b;

                htmlTable += '<tr>'
                    + '<td>' + other + '</td>'
                    + '<td>' + sim + '</td>'
                    + '<td><button class="btn-view" '
                    + 'data-pair-id="' + pairId + '" '
                    + 'data-s1="' + student + '" '
                    + 'data-s2="' + other + '">View diff</button></td>'
                    + '</tr>';
            }}

            htmlTable += '</tbody></table>';
            matchesContainer.innerHTML = htmlTable;
        }}

        function showDiff(pairId, s1, s2) {{
            const allDiffs = document.querySelectorAll('.diff-pair');
            allDiffs.forEach(div => div.style.display = 'none');

            const sourceDiv = document.getElementById(pairId);
            if (!sourceDiv) {{
                diffContainer.innerHTML = '<p class="no-matches">Diff not found for this pair.</p>';
                return;
            }}

            const cloned = sourceDiv.cloneNode(true);
            cloned.style.display = 'block';

            diffContainer.innerHTML = '';
            const title = document.createElement('div');
            title.className = 'diff-pair-title';
            title.textContent = 'Diff view: ' + s1 + ' ↔ ' + s2;
            diffContainer.appendChild(title);
            diffContainer.appendChild(cloned);
        }}

        // Event: öğrenci seçimi
        studentSelect.addEventListener('change', function() {{
            const student = this.value;
            showMatchesForStudent(student);
        }});

        // Event delegation: View diff butonlarına tıklama
        matchesContainer.addEventListener('click', function(e) {{
            const btn = e.target.closest('.btn-view');
            if (!btn) return;

            const pairId = btn.getAttribute('data-pair-id');
            const s1 = btn.getAttribute('data-s1');
            const s2 = btn.getAttribute('data-s2');
            showDiff(pairId, s1, s2);
        }});
    </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML raporu kaydedildi: {output_path}")
