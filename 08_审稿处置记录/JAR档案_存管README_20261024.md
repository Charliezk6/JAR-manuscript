# JAR Source Data — README（存管清单，2026-10-24 第三轮修订后终版哈希）

## 一、当前成品文件（SHA-256 已计算）

JAR档案_Manuscript_修订版_20261024.docx
    686cd6a190e892e92281f873796402708b6d557ac86f940fab2f84e434c6a4f2
JAR档案_DataAvailabilityNote_修订版_20261024.docx
    df8ba10a0bbf49cc0cb2878c1c90a03c8fcf930bfb0cbe888a4b58128c1517b5
JAR档案_Manuscript_修订版_20261024.pdf（LibreOffice 26.8 导出，37 页）
    a164ad38fdbb0965d6066a395a46eb311a069879677342fd320f2aa203437944
JAR档案_DataAvailabilityNote_修订版_20261024.pdf（LibreOffice 26.8 导出，38 页）
    f651fbb6b2371abfe14391bf5cd3ac2b81ad8f220b62e42b6269bf8605412a4b
JAR档案_数据包_定稿_20261023.xlsx（含 2026-10-24 C33 更正：Table 7→Table 6A）
    af06a5c21dffbb01228bb24e484fa2d5dae08afb48488c9b339564f4c6f51b1e
    （C33 更正前备份：_backup_数据包_preC33_20261024.xlsx）

## 二、files 02-17（作者持有的 CSV，打包 JAR_SourceData_CSVs 时填入）

02_估计样本_32208.csv   32,208 x 23   SHA-256: __待填__
03_ESG审计合并面板.csv  33,923 x 34   SHA-256: __待填__
04_审计签字面板.csv     88,851 x 18   SHA-256: __待填__
05_环保处罚_企业年.csv  25,749 x 3    SHA-256: __待填__
06_文本环保度量.csv     969 x 16      SHA-256: __待填__
07_年报审计匹配.csv     1,119 x 17    SHA-256: __待填__
08_华证ESG交叉验证.csv  10,352 x 6    SHA-256: __待填__
09_配对样本_19376.csv   19,376 x 20   SHA-256: __待填__
10-17（结果表 CSV）     行数打包时记录 SHA-256: __待填__（每文件一行）

## 三、表/图 → 文件 → 脚本映射（打包时补脚本名）

- Tables 2A/3-13、A.1-A.8 → 18_主面板（工作簿 sheet）→ 脚本: __待填__
- Table 8 / Table 2A 推断 → 10_联合推断_WCR结果 + 19_Table8联合分解 → 脚本: ext_t8_final.py 等
- Table 12 / A.3-A.6 → 11_稳健性估计 → 脚本: __待填__
- Table 13 / §4.11 → 12_事件研究样本 + 13_修订版表格_事件研究 → 脚本: __待填__
- Table 10 / §4.4 → 14_组合分析 + 20_平衡面板分解 → 脚本: ext_bal_decomp.py
- §4.7 / Table 8.25 → 05 + 16 + 17 → 脚本: __待填__
- Tables A.7-A.8 / A.13 → 21_企业层平衡检验 → 脚本: firm_balance_test.py
- Figures 1-2 → 23_图件作图数据 → 脚本: _fig2_check.py 复算

## 四、许可说明

CSMAR 衍生文件（02-05、07-09、18 中的许可字段）不可再分发；华证分数公开于
Mendeley Data (Lin 2025, DOI: 10.17632/8fh8wtn6p5.2)；公告口径（16/17）来自公开渠道可复现。
