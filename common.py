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
    h2 = h.Clone()

    for iRes, (label, (val, lower, upper)) in enumerate(results):
        iBin = 1 + iRes
        hx.SetBinLabel(iBin, label.replace(tag, ""))
        h.SetBinContent(iBin, (upper + lower) / 2.0)
        h.SetBinError(iBin, (upper - lower) / 2.0)
        h2.SetBinContent(iBin, val)

    h.SetMarkerColor(r.kWhite)
    h.SetMarkerStyle(20)
    h.SetMarkerSize(0.01 * h.GetMarkerSize())
    h.SetMarkerColor(h.GetLineColor())
    h.SetMinimum(yRange[0])
    h.SetMaximum(yRange[1])
    h.Draw("EX0")

    h2.SetMarkerStyle(20)
    h2.SetMarkerColor(h2.GetLineColor())
    h2.SetMarkerSize(0.6 * h2.GetMarkerSize())
    h2.Draw("psame")

    r.gPad.SetGridy()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    canvas.Print(pdf)


def llk_plots(canvas, pdf, tag, yTitle, yRange, rooplots):
    for i, (label, plot) in enumerate(rooplots):
        j = i % 4
        if j == 0:
            canvas.cd(0)
            canvas.Clear()
            canvas.Divide(2, 2)

        canvas.cd(1 + j)
        r.gPad.SetTickx()
        r.gPad.SetTicky()

        title = label.replace(tag, "").replace(";", "#semicolon")
        plot.SetTitle(title)

        r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.FATAL)
        plot.Draw()
        r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG)

        if j == 3 or i == (len(rooplots) - 1):
            canvas.cd(0)
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
            val, lower, upper, plot = func(y)
            results.append((y.label, (val, lower, upper)))
            if plot:
                rooplots.append((y.label, plot))

        one_page(canvas, pdf, tag, yTitle, yRange, results)
        llk_plots(canvas, pdf, tag, yTitle, yRange, rooplots)

    canvas.Print(pdf + "]")
