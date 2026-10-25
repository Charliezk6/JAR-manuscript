* =====================================================================
* JAR manuscript - settle the 52.7 percent question in ONE run.
*
* Section 1 originally said the audit-firm clock "reaches five in the
* same year the partner clock does in 52.7 percent of clock-five
* firm-years".  No pair of deposited counts reproduces that number.
* This do-file computes every plausible reading and reports which, if
* any, reproduces 52.7 - so the question is closed, not argued.
*
* Edit the locals below, then run whole.  Read block (2).
* =====================================================================
use "18_主面板.dta", clear                  // <-- edit path

local firm   stkcd
local yr     year
local pclock CPATenure
local fclock AuditorTenure
local bal    balanced          // 1 if observed in all eleven years
local insamp insample          // 1 if in the 31,274-row estimation sample

capture confirm variable `insamp'
if _rc == 0 {
    keep if `insamp' == 1
    dis "NOTE: restricted to `insamp' == 1"
}
else {
    dis "WARNING: no `insamp' variable - CHECK THIS IS THE 31,274-ROW SAMPLE"
}

gen joint = (`pclock' == 5 & `fclock' == 5)

* ---------------------------------------------------------------------
* (0) Do the deposited constants still hold?
* ---------------------------------------------------------------------
dis _n "--- (0) deposited constants ---"
count
local rows = r(N)
dis "  estimation rows            = `rows'      (want 31,274)"
egen ufirm = tag(`firm')
count if ufirm
dis "  estimation firms           = " r(N) "      (want 4,166)"
count if joint
dis "  joint firm-years           = " r(N) "      (want 2,018)"

count if `pclock' == 5
local n5 = r(N)
dis "  partner-clock-five rows    = `n5'      (memo predicts 4,880-4,900)"

capture confirm variable `bal'
if _rc == 0 {
    count if `pclock' == 5 & `bal' == 1
    dis "  balanced clock-five rows   = " r(N) "      (want 1,887)"
    count if `pclock' == 5 & `fclock' == 5 & `bal' == 1
    dis "  balanced joint rows        = " r(N) "      (want 413)"
    count if `bal' == 1
    dis "  balanced rows total        = " r(N) "      (want 13,122)"
    count if `bal' == 0
    dis "  non-balanced rows total    = " r(N) "      (want 18,152)"
}

* ---------------------------------------------------------------------
* (1) Candidate readings
* ---------------------------------------------------------------------
dis _n "--- (1) candidate readings of the joint share ---"
dis "  definition                                             num       den    share%"
dis "  ------------------------------------------------------------------------"

count if joint
local j = r(N)
dis "  all firm-years                                       " %8.0f `j' "  " %8.0f `rows' "   " %8.2f (100*`j'/`rows')
dis "  clock-five firm-years  <-- manuscript's wording      " %8.0f `j' "  " %8.0f `n5' "   " %8.2f (100*`j'/`n5')

preserve
    keep if `pclock' == 5
    bysort `firm' (`yr'): keep if _n == 1
    count if `fclock' == 5
    local fj = r(N)
    count
    local fn = r(N)
    dis "  firms, joint at FIRST clock-five year               " %8.0f `fj' "  " %8.0f `fn' "   " %8.2f (100*`fj'/`fn') "   (expect 42.34)"
restore

capture confirm variable `bal'
if _rc == 0 {
    foreach g in 0 1 {
        count if `pclock' == 5 & `bal' == `g'
        local dg = r(N)
        count if joint & `bal' == `g'
        local jg = r(N)
        local lab = cond(`g' == 0, "non-balanced", "balanced    ")
        dis "  clock-five firm-years, `lab'                        " %8.0f `jg' "  " %8.0f `dg' "   " %8.2f (100*`jg'/`dg')
    }
}

foreach rng in "2013 2021 pre-repeal" "2022 2023 post-repeal" "2013 2019 2013-2019" "2020 2021 2020-2021" {
    local lo : word 1 of `rng'
    local hi : word 2 of `rng'
    local lb : word 3 of `rng'
    count if `pclock' == 5 & `yr' >= `lo' & `yr' <= `hi'
    local dg = r(N)
    count if joint & `yr' >= `lo' & `yr' <= `hi'
    local jg = r(N)
    dis "  clock-five firm-years, `lb'                        " %8.0f `jg' "  " %8.0f `dg' "   " %8.2f (100*`jg'/`dg')
}

* ---------------------------------------------------------------------
* (2) Adjudication
* ---------------------------------------------------------------------
dis _n "--- (2) ADJUDICATION ---"
dis "  Look through the share column for a value within 0.15 of 52.70."
dis "  If none: 52.7 belongs to a sample vintage that is not the deposited"
dis "  one - it is stale and must not be reinstated.  The current Section 1"
dis "  text (1,764 of 4,166 firms; 53.4 / 21.9 by persistence) does not"
dis "  depend on the total count of clock-five firm-years, so it stands"
dis "  whatever this run returns."
dis "  If one matches: that denominator is what the old sentence was using,"
dis "  and you can decide whether it is the one a reader should verify."
dis ""
dis "  Cross-check on the derivation: full-sample share should be about"
dis "  2,018 / `n5' = " %5.2f (100*2018/`n5') " percent. The memo predicts ~41."

* =====================================================================
* pairsym zero-padding (data-package item; run before re-depositing 18)
* =====================================================================
gen  ps_name = substr(pairsym, 1, strpos(pairsym, "||") - 1)
gen  ps_code = substr(pairsym, strpos(pairsym, "||") + 2, .)
replace ps_code = string(real(ps_code), "%06.0f") if real(ps_code) < .
replace pairsym = ps_name + "||" + ps_code
drop ps_name ps_code
* "||" is safe inside a quoted CSV field, but any downstream tool that
* splits on "|" will shred it. Consider "#" if you re-deposit.
