* =====================================================================
* JAR manuscript - settle the 52.7 percent question and complete
* Table 6A.  Run on the primary estimation sample (31,274 firm-years).
*
* Edit the three `local`s below to your variable names, then run whole.
* Expected results are in the comments; anything else means one of the
* deposited figures needs re-checking.
* =====================================================================
use "18_主面板.dta", clear                  // <-- edit path

local pclock pclock      // partner clock (longer-serving signing partner)
local fclock fclock      // audit-firm clock (CSMAR AuditorTenure)
local bal    bal         // 1 if the firm is observed in all eleven years

keep if tenure >= 1 & tenure <= 5           // primary firm-year sample

* ---------------------------------------------------------------------
* (a) Full-sample joint share of clock-five firm-years
*     DECISION RULE: if `n5' falls between 4,880 and 4,900, the
*     full-sample share is about 41 percent and the manuscript's
*     52.7 percent is a scope error (the non-balanced 53.4 percent
*     was written into a full-sample sentence).
* ---------------------------------------------------------------------
count if `pclock' == 5
local n5 = r(N)
count if `pclock' == 5 & `fclock' == 5
local j5 = r(N)
dis _n "--- (a) full sample ---"
dis "clock-five firm-years       = `n5'      (expect 4,880-4,900)"
dis "joint clock-five firm-years = `j5'      (expect 2,018)"
dis "full-sample joint share     = " 100*`j5'/`n5' " percent   (expect ~41)"

* ---------------------------------------------------------------------
* (b) Split by panel persistence - should reproduce 53.4 and 21.9
* ---------------------------------------------------------------------
dis _n "--- (b) by panel persistence ---"
foreach g in 0 1 {
    count if `pclock' == 5 & `bal' == `g'
    local d = r(N)
    count if `pclock' == 5 & `fclock' == 5 & `bal' == `g'
    dis "bal=`g': clock-five rows = `d'    joint share = " 100*r(N)/`d' " percent"
}
* expect   bal=0 -> 53.4      bal=1 -> 21.9 (1,887 rows, 413 joint)

* ---------------------------------------------------------------------
* (c) Firm-year cross-tabulation of the two clocks
*     (the firm-year counterpart of Table 6A Panel A)
* ---------------------------------------------------------------------
dis _n "--- (c) firm-year crosstab ---"
tab `fclock' `pclock' if `pclock' <= 5 & `fclock' <= 5, cell
tab `fclock' `pclock' if `pclock' <= 5 & `fclock' <= 5, row

* ---------------------------------------------------------------------
* (d) Firm-level split of firm clock 2 and 3
*     Resolves the one combined row in Table 6A Panel A (234 firms).
* ---------------------------------------------------------------------
dis _n "--- (d) firm-level, first clock-five year ---"
preserve
    keep if `pclock' == 5
    bysort firm (year): keep if _n == 1
    tab `fclock', miss
    * expect: 1 -> 101 ; 2+3 -> 234 ; 4 -> 128 ; 5 -> 1,764 ;
    *         6 -> 173 ; 7 -> 157 ; 8-19 -> 666 ; total 4,166
restore

* =====================================================================
* pairsym zero-padding (data-package item; run on the panel before
* re-depositing file 18).  The field is  "name1,name2||code"  with an
* unpadded numeric stock code such as ||6, which contradicts the
* "uniformly zero-padded six-character string" statement in DAN 9(i)
* and manuscript A.7(i).
* =====================================================================
gen  ps_name = substr(pairsym, 1, strpos(pairsym, "||") - 1)
gen  ps_code = substr(pairsym, strpos(pairsym, "||") + 2, .)
replace ps_code = string(real(ps_code), "%06.0f") if real(ps_code) < .
replace pairsym = ps_name + "||" + ps_code
drop ps_name ps_code
* NOTE: "||" is safe inside a quoted CSV field, but any downstream tool
* that splits on "|" will shred it. If you re-deposit, consider "#".
