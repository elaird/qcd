#!/usr/bin/env python

import ROOT as r
import common


class yields(object):
    def __init__(self, label="",
                 n_SST=None, ewk_SST=None,
                 n_SSL=None, ewk_SSL=None,
                 n_M=None, ewk_M=None,
                 ):
        self.label = label
        for l in ["M", "SSL", "SST"]:
            for item in ["n", "ewk"]:
                s = "%s_%s" % (item, l)
                setattr(self, s, eval(s))
    

def data():
    return [yields("1;M;   one  1~4",  25,  1.49,    106,  5.45,   127, 19.29),
            yields("1;L;   one  1~4", 102,  2.07,    390,  6.78,   127, 19.29),
            yields("2;M;   one  1~4",   2,  0.43,      4,  2.10,    22,  5.90),
            yields("2;L;   one  1~4",  20,  1.24,     97,  7.35,    22,  5.90),
            yields("1;M;  both  1~4",  25,  1.49,     73,  3.89,   109,  5.77),
            yields("1;L;  both  1~4", 102,  2.07,    367,  4.16,   109,  5.77),
            yields("2;M;  both  1~4",   2,  0.43,      9,  1.09,    10,  2.39),
            yields("2;L;  both  1~4",  20,  1.24,     87,  3.57,    10,  2.39),
            yields("1;M;   one 3~10",  25,  1.49,    307, 19.26,   392, 33.41),
            yields("1;L;   one 3~10", 102,  2.07,   1154, 20.82,   392, 33.41),
            yields("2;M;   one 3~10",   2,  0.43,     29,  3.90,    42, 13.05),
            yields("2;L;   one 3~10",  20,  1.24,    304, 16.75,    42, 13.05),
            yields("1;M;  both 3~10",  25,  1.49,    845, 22.18,   884, 29.64),
            yields("1;L;  both 3~10", 102,  2.07,   3174, 19.13,   884, 29.64),
            yields("2;M;  both 3~10",   2,  0.43,     68,  7.57,    74, 12.24),
            yields("2;L;  both 3~10",  20,  1.24,    913, 23.06,    74, 12.24),
        ]


def arithmetic(y):
    assert y.n_SST
    val = (y.n_M - y.ewk_M) * (y.n_SST - y.ewk_SST) / (y.n_SSL - y.ewk_SSL)
    err = val * r.TMath.sqrt(y.n_SST) / y.n_SST
    return val, err


def fit_qcd(y):
    # Pois(n_M | ewk_M + qcd/r2) x Pois(n_SST | ewk_SST + r2*q_SSL) x Pois(n_SSL | ewk_SSL + q_SSL)

    w = r.RooWorkspace("Workspace")
    wimport = common.wimport
    wimport(w, r.RooRealVar("r", "r", 0.2, 0.0, 1.0))  # r2 above
    wimport(w, r.RooRealVar("qcd_SSL", "qcd_SSL", y.n_SSL, 0.0, 10.0 * max(1.0, y.n_SSL)))
    wimport(w, r.RooRealVar("qcd", "qcd", y.n_SST, 0.0, 10.0 * max(1.0, y.n_SST)))

    for l in ["M", "SSL", "SST"]:
        wimport(w, r.RooRealVar("ewk_%s" % l, "ewk_%s" % l, getattr(y, "ewk_%s" % l)))
        wimport(w, r.RooRealVar("n_%s" % l, "n_%s" % l, getattr(y, "n_%s" % l)))

    wimport(w, r.RooFormulaVar("mean_SSL", "(@0)+(@1)", r.RooArgList(w.var("ewk_SSL"), w.var("qcd_SSL"))))
    wimport(w, r.RooFormulaVar("mean_SST", "(@0)+((@1)*(@2))", r.RooArgList(w.var("ewk_SST"), w.var("qcd_SSL"), w.var("r"))))
    wimport(w, r.RooFormulaVar("mean_M",   "(@0)+((@1)/(@2))", r.RooArgList(w.var("ewk_M"), w.var("qcd"), w.var("r"))))

    for l in ["M", "SSL", "SST"]:
        wimport(w, r.RooPoisson("pois_%s" % l, "pois_%s" % l, w.var("n_%s" % l), w.function("mean_%s" % l)))

    w.factory("PROD::model(pois_M,pois_SSL,pois_SST)")

    w.defineSet("obs", common.argSet(w, ["n_M", "n_SSL", "n_SST"]))
    #w.Print()

    res = common.fit(pdf=w.pdf("model"), obsSet=w.set("obs"))
    #res.Print()

    var = w.var("qcd")
    return (var.getVal(), var.getError())


if __name__ == "__main__":
    common.setup()

    __qcd = {"data": data, "yTitle": "QCD yield estimate"}
    common.go(pdf="QCD_arithmetic1.pdf", func=arithmetic, tags=["1;"], yRange=(0.0, 40.0), **__qcd)
    common.go(pdf="QCD_arithmetic2.pdf", func=arithmetic, tags=["2;"], yRange=(0.0, 15.0), **__qcd)
    common.go(pdf="QCD_fit1.pdf", func=fit_qcd, tags=["1;"], yRange=(0.0, 40.0), **__qcd)
    common.go(pdf="QCD_fit2.pdf", func=fit_qcd, tags=["2;"], yRange=(0.0, 15.0), **__qcd)
