#!/usr/bin/env python

import ROOT as r


def wimport(w, item):
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING)  # suppress info messages
    if item.ClassName() == "RooPoisson":
        item.protectNegativeMean()
        item.setNoRounding()
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG)  # re-enable all messages


class yields(object):
    def __init__(self, label="",
                 n_M=None, ewk_M=None, k_ewk_M=None,
                 n_L=None, ewk_L=None, k_ewk_L=None,
                 ):
        self.label = label
        for l in ["M", "L"]:
            for item in ["n", "ewk", "k_ewk"]:
                s = "%s_%s" % (item, l)
                setattr(self, s, eval(s))
                 
    

def data_CSV_L2M():
    e = 0.01
    return [yields("1tag; one  1~4, OS", 127, 19.29, e,  531, 31.22, e),
            yields("1tag; one  1~4, SS", 106,  5.45, e,  390,  6.78, e),
            yields("2tag; one  1~4, OS",  22,  5.90, e,  139, 19.28, e),
            yields("2tag; one  1~4, SS",   4,  2.10, e,   97,  7.35, e),
            yields("1tag;both  1~4, OS", 109,  5.77, e,  451,  9.42, e),
            yields("1tag;both  1~4, SS",  73,  3.89, e,  367,  4.16, e),
            yields("2tag;both  1~4, OS",  10,  2.39, e,  125,  5.66, e),
            yields("2tag;both  1~4, SS",   9,  1.09, e,   87,  3.57, e),
            yields("1tag; one 3~10, OS", 392, 33.41, e, 1375, 40.04, e),
            yields("1tag; one 3~10, SS", 307, 19.26, e, 1154, 20.82, e),
            yields("2tag; one 3~10, OS",  42, 13.05, e,  426, 34.53, e),
            yields("2tag; one 3~10, SS",  29,  3.90, e,  304, 16.75, e),
            yields("1tag;both 3~10, OS", 884, 29.64, e, 3573, 25.03, e),
            yields("1tag;both 3~10, SS", 845, 22.18, e, 3174, 19.13, e),
            yields("2tag;both 3~10, OS",  74, 12.24, e,  972, 30.49, e),
            yields("2tag;both 3~10, SS",  68,  7.57, e,  913, 23.06, e),
        ]


def data_SS_relaxed_to_tight():
    e = 0.01
    return [yields("1;M; one  1~4, SS",  25,  1.49, e,  106,  5.45, e),
            yields("2;M; one  1~4, SS",   2,  0.43, e,    4,  2.10, e),
            yields("1;L; one  1~4, SS", 102,  2.07, e,  390,  6.78, e),
            yields("2;L; one  1~4, SS",  20,  1.24, e,   97,  7.35, e),
            yields("1;M;both  1~4, SS",  25,  1.49, e,   73,  3.89, e),
            yields("2;M;both  1~4, SS",   2,  0.43, e,    9,  1.09, e),
            yields("1;L;both  1~4, SS", 102,  2.07, e,  367,  4.16, e),
            yields("2;L;both  1~4, SS",  20,  1.24, e,   87,  3.57, e),
            yields("1;M; one 3~10, SS",  25,  1.49, e,  307, 19.26, e),
            yields("2;M; one 3~10, SS",   2,  0.43, e,   29,  3.90, e),
            yields("1;L; one 3~10, SS", 102,  2.07, e, 1154, 20.82, e),
            yields("2;L; one 3~10, SS",  20,  1.24, e,  304, 16.75, e),
            yields("1;M;both 3~10, SS",  25,  1.49, e,  845, 22.18, e),
            yields("2;M;both 3~10, SS",   2,  0.43, e,   68,  7.57, e),
            yields("1;L;both 3~10, SS", 102,  2.07, e, 3174, 19.13, e),
            yields("2;L;both 3~10, SS",  20,  1.24, e,  913, 23.06, e),
        ]


def fit(pdf=None, data=None):
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG)
    options = [r.RooFit.Verbose(False),
               r.RooFit.PrintLevel(-1),
               r.RooFit.Save(True),
               #r.RooFit.Minos(True),
           ]
    return pdf.fitTo(data, *tuple(options))


def argSet(w=None, vars=[]):
    out = r.RooArgSet("out")
    for item in vars:
        out.add(w.var(item))
    return out


def dataset(obsSet):
    out = r.RooDataSet("dataName", "dataTitle", obsSet)
    #out.reset() #needed?
    out.add(obsSet)
    #out.Print("v")
    return out


def arithmetic(y):
    assert y.n_M
    val = (y.n_M - y.ewk_M) / (y.n_L - y.ewk_L)
    err = val * r.TMath.sqrt(y.n_M) / y.n_M
    return val, err


def fit_two_terms(y):
    # Pois(n_M | ewk_M + r*q_L) x Pois(n_L | ewk_L + q_L)

    w = r.RooWorkspace("Workspace")
    wimport(w, r.RooRealVar("r", "r", 0.2, -1.0, 1.0))  # parameter of interest: loose to medium factor
    wimport(w, r.RooRealVar("qcd_L", "qcd_L", y.n_L, 0.0, 10.0 * max(1.0, y.n_L)))

    for l in ["M", "L"]:
        wimport(w, r.RooRealVar("ewk_%s" % l, "ewk_%s" % l, getattr(y, "ewk_%s" % l)))
        wimport(w, r.RooRealVar("n_%s" % l, "n_%s" % l, getattr(y, "n_%s" % l)))

    wimport(w, r.RooFormulaVar("mean_L", "(@0)+(@1)", r.RooArgList(w.var("ewk_L"), w.var("qcd_L"))))
    wimport(w, r.RooFormulaVar("mean_M", "(@0)+((@1)*(@2))", r.RooArgList(w.var("ewk_M"), w.var("r"), w.var("qcd_L"))))

    for l in ["M", "L"]:
        wimport(w, r.RooPoisson("pois_%s" % l, "pois_%s" % l, w.var("n_%s" % l), w.function("mean_%s" % l)))

    w.factory("PROD::model(pois_L,pois_M)")
    w.defineSet("obs", argSet(w, ["n_L", "n_M"]))
    #w.Print()
    res = fit(pdf=w.pdf("model"), data=dataset(w.set("obs")))
    res.Print()
    rVar = w.var("r")
    return (rVar.getVal(), rVar.getError())


def one_page(canvas, pdf, tag, yTitle, yRange, results):
    h = r.TH1D("h", "%s;%s" % (tag, yTitle), len(results), 0.0, len(results))
    h.SetStats(False)
    hx = h.GetXaxis()
    h.GetYaxis().SetTitleOffset(1.25)

    for iRes, (label, (val, err)) in enumerate(results):
        iBin = 1 + iRes
        hx.SetBinLabel(iBin, label.replace(tag, ""))
        h.SetBinContent(iBin, val)
        h.SetBinError(iBin, err)
    h.Draw()
    h.SetMinimum(yRange[0])
    h.SetMaximum(yRange[1])
    r.gPad.SetGridy()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    canvas.Print(pdf)


def go(pdf="", tags=[], yTitle="", yRange=None, func=None, data=None):
    canvas = r.TCanvas()
    canvas.Print(pdf + "[")

    for tag in tags:
        results = []
        for y in data():
            if tag not in y.label:
                continue
            results.append((y.label, func(y)))
        one_page(canvas, pdf, tag, yTitle, yRange, results)

    canvas.Print(pdf + "]")

    
if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = r.kWarning
    r.gPrintViaErrorHandler = True
    r.RooRandom.randomGenerator().SetSeed(1)

    __L2M = {"yRange": (-0.02, 0.32),
             "yTitle": "CSVL to CSVM",
             "data": data_CSV_L2M,
             "tags": ["1tag;", "2tag;"]}

    go(pdf="L2M_fit.pdf", func=fit_two_terms, **__L2M)
    go(pdf="L2M_arithmetic.pdf", func=arithmetic, **__L2M)

    __R2T = {"yRange": (-0.1, 1.0),
             "yTitle": "relaxed to tight",
             "data": data_SS_relaxed_to_tight,
             "tags": ["1;", "2;"]}

    go(pdf="R2T_fit.pdf", func=fit_two_terms, **__R2T)
    go(pdf="R2T_arithmetic.pdf", func=arithmetic, **__R2T)