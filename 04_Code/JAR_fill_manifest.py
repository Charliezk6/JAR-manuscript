# JAR_fill_manifest.py — 作者工具：在存放 files 02-17（JAR_SourceData_CSVs）的目录中运行，
# 自动计算每个文件的行数、列数与 SHA-256，生成可直接粘贴进 DAN §9.1 与存管 README 的清单表。
#
# 用法：  python JAR_fill_manifest.py [目录]      （默认当前目录）
# 输出：  manifest_filled.csv + manifest_filled.md（同目录）

import csv
import hashlib
import os
import sys

TARGETS = [
    "00_源文件清单.csv", "01_变量字典.csv", "02_估计样本_32208.csv", "03_ESG审计合并面板.csv",
    "04_审计签字面板.csv", "05_环保处罚_企业年.csv", "06_文本环保度量.csv", "07_年报审计匹配.csv",
    "08_华证ESG交叉验证.csv", "09_配对样本_19376.csv", "10_联合推断_WCR结果.csv", "11_稳健性估计.csv",
    "12_事件研究样本.csv", "13_修订版表格_事件研究.csv", "14_组合分析.csv", "15_扩展检验_三项.csv",
    "16_环境处罚公告_企业年.csv", "17_环境处罚公告_估计.csv",
]

REPRODUCES = {
    "00_源文件清单.csv": "This manifest",
    "01_变量字典.csv": "All tables; variable list",
    "02_估计样本_32208.csv": "Tables 3-8, 10-13",
    "03_ESG审计合并面板.csv": "Supplement S1; Section 8.24",
    "04_审计签字面板.csv": "Table 2 funnel; clocks",
    "05_环保处罚_企业年.csv": "Section 4.7; Table 8.4",
    "06_文本环保度量.csv": "Section 4.8",
    "07_年报审计匹配.csv": "Section 4.8",
    "08_华证ESG交叉验证.csv": "Section 8.24",
    "09_配对样本_19376.csv": "Tables 8-9",
    "10_联合推断_WCR结果.csv": "Table 8 inference",
    "11_稳健性估计.csv": "Table 12; A.3-A.6",
    "12_事件研究样本.csv": "Section 4.11",
    "13_修订版表格_事件研究.csv": "Table 13",
    "14_组合分析.csv": "Table 10",
    "15_扩展检验_三项.csv": "Sections 4.7, 4.12, 4.13",
    "16_环境处罚公告_企业年.csv": "Section 4.7; Table 8.25",
    "17_环境处罚公告_估计.csv": "Section 4.7",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(root):
    rows = []
    missing = []
    for name in TARGETS:
        p = os.path.join(root, name)
        if not os.path.exists(p):
            missing.append(name)
            continue
        with open(p, encoding="utf-8-sig", errors="replace") as f:
            reader = csv.reader(f)
            header = next(reader)
            ncols = len(header)
            nrows = 1 + sum(1 for _ in reader)
        rows.append({
            "file": name,
            "rows": nrows,
            "cols": ncols,
            "reproduces": REPRODUCES[name],
            "sha256": sha256(p),
            "bytes": os.path.getsize(p),
        })

    csv_out = os.path.join(root, "manifest_filled.csv")
    with open(csv_out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["file", "rows", "cols", "reproduces", "sha256", "bytes"])
        w.writeheader()
        w.writerows(rows)

    md_out = os.path.join(root, "manifest_filled.md")
    with open(md_out, "w", encoding="utf-8") as f:
        f.write("# files 00-17 实测清单（自动生成，供 DAN §9.1 与存管 README 使用）\n\n")
        f.write("| File | Rows x cols | Reproduces | SHA-256 |\n|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['file']} | {r['rows']} x {r['cols']} | {r['reproduces']} | `{r['sha256']}` |\n")
        if missing:
            f.write("\n缺失文件: " + ", ".join(missing) + "\n")

    print(f"处理 {len(rows)} 个文件；缺失 {len(missing)}: {missing or '无'}")
    print("已生成:", csv_out)
    print("已生成:", md_out)
    print("\n预览：")
    with open(md_out, encoding="utf-8") as f:
        print(f.read())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
