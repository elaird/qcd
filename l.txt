Full L
------
Pois(n_M | ewk_M + r1*q_L) x Pois(n_L | ewk_L + q_L) x 

Pois(n_SST | ewk_SST + r2*q_SSL) x Pois(n_SSL | ewk_SSL + q_SSL)

with qcd = q_L * r1 * r2


Simplification
--------------
assume shape is unit-normalized via q_L; then L = 

Pois(n_M | ewk_M + q_M) x Pois(n_SST | ewk_SST + r2*q_SSL) x Pois(n_SSL | ewk_SSL + q_SSL)

with qcd = q_M * r2


Reparametrization
-----------------
Pois(n_M | ewk_M + qcd/r2) x Pois(n_SST | ewk_SST + r2*q_SSL) x Pois(n_SSL | ewk_SSL + q_SSL)

with floating variables (qcd, r2, q_SSL); restrict 0 < r2
