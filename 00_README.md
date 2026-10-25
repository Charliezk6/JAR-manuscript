# JAR Replication Package — 2026-10-24

Manuscript: Joint Signing-Partner and Audit-Firm Tenure and Environmental Disclosure:
Evidence from Completing Partner Spells
Target journal: Journal of Accounting Research (Wiley Research Exchange)

## 目录结构

01_Manuscript/            修订版正文（docx + PDF，37 页）
02_DataAvailabilityNote/  修订版数据说明（docx + PDF，38 页）
03_Data/                  数据包工作簿（xlsx，sheet 00-23）+ 各工作表 CSV
04_Code/                  复现代码：作者原脚本（05_复现代码）+ 本轮核查脚本
                          (compute_2x2.py, compute_penalty*.py, verify_file15b.py)
                          + JAR_fill_manifest.py（打包 02-17 时运行的清单工具）
05_Figures/               Figure 1-2 的 SVG 源文件与 PNG
06_Results_QC/            结果 JSON 与质控记录
07_Submission/            Cover letter、Title page、Highlights、Data Availability
                          Statement、Submission checklist（作者信息为高亮占位符）
08_审稿处置记录/          四轮审稿意见逐条处置清单 + 存管 README

## 质控验证记录（2026-10-24，verify_file15b.py）

从作者估计框架 _est31k.pkl（31,274 行 × 59 列）以双向固定效应 + 企业聚类 CR1 复算：

| 量 | 复算值 | 论文值 | 判定 |
|---|---|---|---|
| Table 4 E 落差（校准用） | 0.646, t = 7.44 | 0.646, t = 7.44 | 一致 |
| 宽旗标事件数（2013-2020 主样本窗口） | 1,414 / 20,079 = 7.04% | 1,414 / 7.04% | 一致 |
| 登记口径事件数（同窗口） | 204 / 1.02% | 204 / 1.02% | 一致 |
| 宽旗标 Y4−Y5 落差 | 1.46 pp, t = 2.68 | +1.458 pp, t = 2.68 | 一致 |
| 2017/2018 年基率 | 17.6% / 19.9% | 17.6% / 19.9% | 一致 |
| 2×2（平衡×联合，五年行） | 1,887/413；3,004/1,605；合计 4,891 = 2,018 | 同 | 一致 |

结论：file 15 相关数值已从底层框架端到端复现，无需再人工眼验。

## 打包 JAR_SourceData_CSVs 时（作者最后一步）

1. 把 files 02-17 的 CSV 放到一个目录；
2. 运行 `python JAR_fill_manifest.py <目录>`（自动生成 manifest_filled.csv/.md，含行数、列数、SHA-256）；
3. 把 manifest_filled.md 的表格粘进 DAN §9.1 与存管 README 对应位置。

## 许可

CSMAR 衍生数据不随包重分发（05_复现代码 + 03_Data 的非许可字段可复现全部表格）；
华证 ESG 分数公开于 Mendeley Data (Lin 2025, DOI: 10.17632/8fh8wtn6p5.2)。


## 本包文件哈希（SHA-256，随本包最终内容生成）
686cd6a190e892e92281f873796402708b6d557ac86f940fab2f84e434c6a4f2  01_Manuscript/JAR档案_Manuscript_修订版_20261024.docx
a164ad38fdbb0965d6066a395a46eb311a069879677342fd320f2aa203437944  01_Manuscript/JAR档案_Manuscript_修订版_20261024.pdf
df8ba10a0bbf49cc0cb2878c1c90a03c8fcf930bfb0cbe888a4b58128c1517b5  02_DataAvailabilityNote/JAR档案_DataAvailabilityNote_修订版_20261024.docx
f651fbb6b2371abfe14391bf5cd3ac2b81ad8f220b62e42b6269bf8605412a4b  02_DataAvailabilityNote/JAR档案_DataAvailabilityNote_修订版_20261024.pdf
af06a5c21dffbb01228bb24e484fa2d5dae08afb48488c9b339564f4c6f51b1e  03_Data/JAR档案_数据包_定稿_20261023.xlsx
6e28108ba9663a9f410c44642a3c47822be1ebcdc44a6bb19056f7571c8e603f  03_Data/各工作表CSV/00_索引.csv
50c1a3cc41071bb66cbbbd4fb9ae1980721ff47ac43acd5e4b08a85449de03c2  03_Data/各工作表CSV/01_变量字典.csv
a2eb10bb2fcc828d5e8ef60f7d77fc6ec9623c772d70e94cdc5be913982f8b6b  03_Data/各工作表CSV/18_主面板.csv
00fb47edde2d574e0d9530eec4cf1aabe77421fd5b5a8efd880cde79ae749aa7  03_Data/各工作表CSV/19_Table8联合分解.csv
7969181d0396c976bf92ae2d68bfd96547cf4ff1cde1a2cf788d77f43edeb5e0  03_Data/各工作表CSV/20_平衡面板分解.csv
4519255ed9143314b460964348398847cc43b7a3d56ec78dec373389c926095d  03_Data/各工作表CSV/21_企业层平衡检验.csv
106196fc0036c9b0c25631fba74111a72c16b0b6b475ef8e5a04a1b9747f3f6e  03_Data/各工作表CSV/22_正文表格数值.csv
6fc72979d0e47ef1b736413888945dc537758a03a4a4adc5274ccffadd4f80ce  03_Data/各工作表CSV/23_图件作图数据.csv
22a13e2bc9f9724712fae558d86311ab09e8d2f12e76ce46aa7e0b3d77cf4d6e  04_Code/JAR_fill_manifest.py
91c374509456588c01e0ad3bd79ee27201e2e92c9f34a6762655daf90e0140a9  04_Code/compute_2x2.py
a706d4df2a8452adf15d6f2df247d3511aa0e44dde1de0caee7f43a086ef6b90  04_Code/compute_penalty.py
53eead834ac012f3b321264625f967320120024cc9dc57f16592dd648e0fdc1d  04_Code/compute_penalty_year.py
aa939198e7d62a102ffd0d68411094c482e801a461537738fc26d78533f95577  04_Code/verify_file15b.py
e25cd0dbfd10fd14d1fdedb9cec1376ff72366f9d8d3535c496296816b5640d5  04_Code/05_复现代码/_fb_final.py
1f98d7ebf5802ca0345997918765e138c7e69f637ef85b6b9dfd6d48ac0f87c3  04_Code/05_复现代码/_fb_phase01.py
a55ea06327d404b3b55722287072b748b1b90e8debb8886bec66d8571e49ab04  04_Code/05_复现代码/_fb_phase01b.py
906ecb685926645b834868782e9f4856b36887f5d14979bfa18f36b789fd38f3  04_Code/05_复现代码/_fb_phase02.py
a7fe60b9fbce733d16c627e311edcb257a760d3594952d28f9c9ca5fe6e05522  04_Code/05_复现代码/_fb_phase345.py
c631111b1bc64c894e755c272fbd3c9712b5428ce6d338cd70b43e95cd0e808e  04_Code/05_复现代码/_fig2_check.py
6421184f80a606eb73cd7e975a8a19af10237cda7c43ee299f3142f65a5ad788  04_Code/05_复现代码/_figures.py
cc8c4625ea74832078bd7103e9659d067fe88749cdebf3022904218af8069801  04_Code/05_复现代码/_figures_png.py
a668aea6e835684cdd56fb08f5974245e404b40d14e625c94484c77418a88c0c  04_Code/05_复现代码/_pkg_v13.py
0d363b3fdd52903681a71ac696cc0d3c14cf092706eac9049aa26bc7dc6cf3ac  04_Code/05_复现代码/_pkgdoc_add22b.py
c8b29e624d389c863c61eeaff260fcb0551342047d5790d576a1d036e85e2ff8  04_Code/05_复现代码/_recount.do
0988eabc0fedb418bd8dea069a116b5a73ac070d6d2dd2af3ce59c949ca0739d  04_Code/05_复现代码/_recount.py
626c74fe34cb9a41113effe8b6a41cc05d4a5bf1711e5c2038e7f1e2e9fbf1eb  04_Code/05_复现代码/_recount52.do
882893000730409302e576181c7e23d245a53c05ea4fd22ff70b8b1144b44e4a  04_Code/05_复现代码/_recount52.py
e25cd0dbfd10fd14d1fdedb9cec1376ff72366f9d8d3535c496296816b5640d5  04_Code/05_复现代码/firm_balance_test.py
0bc5362fbfa5b7f1668b00a471584f067f5302e8a40439a450a0bdae53efaaad  05_Figures/04_图件/JAR档案_Figure1_20261023.svg
b571f5cd143ec4f53394c703658e4f3449247cd354aedc4bb8af0f6e7c51154b  05_Figures/04_图件/JAR档案_Figure2_20261023.svg
ab31d0eed51c1c31a5c7ae973f5284ccc4f2c7dc7570f2e851005942a65c8782  05_Figures/04_图件/JAR档案_Figures预览_20261023.html
fb03274d94d6bd30c1f5599446f0c271428b84d559c4b9b6b7afa7595a345dbd  05_Figures/04_图件/JAR档案_稿件内嵌原图_Figure1.png
2a692b246ec736f5dcb1e3d1158c2c30041c5419ffa71d3270cd3e413ea8053d  05_Figures/04_图件/JAR档案_稿件内嵌原图_Figure2.png
6dea4baffb7f2bf50b8da7bdc0aea569305302aa7ce397ae0549259be4006884  06_Results_QC/06_结果数据/fig2_numbers.json
26ea9bc260dcbafc1f551d92d8797b5885a988211c50483dc32015c6b25f8269  06_Results_QC/06_结果数据/firm_balance_results.json
7b99c37bd499a4a5c6155ec082bc8b114a5f21a7dbfc644d259f2147a92b755a  07_Submission/Cover_Letter_JAR_20261024.docx
2edf0c3e3726b32b5c89c96e1cd6acf2386ee92c5b9867282e21620c0a0bffb1  07_Submission/Data_Availability_Statement_20261024.docx
5bfa8b84addf69b0bcfc6e9e9b53881685700871d27449cc9e9b0f34f9a04ad5  07_Submission/Highlights_Key_Findings_20261024.docx
98aeedba43fa74dc66d32c8e88624ff2f38357ed0d16ce0185a03cf8edce3f61  07_Submission/Submission_Checklist_20261024.docx
a1e4c9ff3a66e789b8b41c49c3eb9b33435c83767e6fbfc9b8aa3368d48afdc2  07_Submission/Title_Page_20261024.docx
d6611e2290c8d768881ec593ff46aae762e950c5a4720c567e4e028259192f9f  08_审稿处置记录/JAR档案_存管README_20261024.md
09a100a620dac06543bf51c6e490fd0abe0ebff18aaaa3d0e09eec1eb4284af8  08_审稿处置记录/JAR档案_审稿意见处置清单_20261024.docx
