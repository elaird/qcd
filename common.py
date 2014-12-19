import ROOT as r


def setup():
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = r.kWarning
    r.gPrintViaErrorHandler = True
    r.RooRandom.randomGenerator().SetSeed(1)


def wimport(w, item):
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING)  # suppress info messages
    if item.ClassName() == "RooPoisson":
        item.protectNegativeMean()
        item.setNoRounding()
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG)  # re-enable all messages


def fit(pdf=None, dataset=None):
    options = [r.RooFit.Verbose(False),
               r.RooFit.PrintLevel(-1),
               r.RooFit.Save(True),
               #r.RooFit.Minos(True),
           ]
    return pdf.fitTo(dataset, *tuple(options))


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
        rooplots = []
        for y in data():
            if tag not in y.label:
                continue
            val, err, plot = func(y)
            rooplots.append((y.label, plot))
            results.append((y.label, (val, err)))
        one_page(canvas, pdf, tag, yTitle, yRange, results)

        for label, plot in rooplots:
            if not plot:
                continue

            r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.FATAL)
            plot.Draw()
            r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG)

            r.gPad.SetTickx()
            r.gPad.SetTicky()
            canvas.Print(pdf)


    canvas.Print(pdf + "]")
