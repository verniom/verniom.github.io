import asyncio, sys
from playwright.async_api import async_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8765/"
OUT="/workspace/verniom-site/shots/"
async def flow(b,w,h,tag,block,shots):
    ctx=await b.new_context(viewport={"width":w,"height":h},device_scale_factor=2,accept_downloads=True)
    if block: await ctx.route("**/abacus.jasoncameron.dev/**",lambda r:r.abort())
    pg=await ctx.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.on("console",lambda m:errs.append(m.text) if m.type=="error" and "abacus" not in m.text and "net::" not in m.text and "Failed to load resource" not in m.text else None)
    pg.on("dialog",lambda d:asyncio.ensure_future(d.accept()))
    async def shot(name,full=False):
        if name in shots: await pg.screenshot(path=OUT+f"{tag}-{name}.png",full_page=full)
    await pg.goto(BASE+"demo/",wait_until="networkidle")
    await pg.fill("input[name=comm]","1.5")
    await pg.click("[data-t=create]"); await pg.wait_for_selector("[data-amt]")
    await pg.click("[data-amt='5000']"); await pg.click("[data-t=pay]"); await pg.wait_for_selector("[data-t=to3]",timeout=8000)
    await pg.click("[data-t=to3]"); await pg.click("[data-mode=own]"); await pg.click("[data-t=widget]"); await pg.wait_for_selector("pre.code")
    await pg.click("[data-mode=new]"); await pg.click("[data-t=publish]")
    await pg.wait_for_selector("[data-buy]",timeout=8000)
    await pg.click("[data-buy='5']"); await pg.click("[data-t=buyok]")
    await pg.wait_for_selector("[data-lk]",timeout=8000); await pg.wait_for_timeout(700)
    await shot("1-purchase-sms",True)
    await pg.click("#smsbox [data-lk]"); await pg.wait_for_selector("#pin")
    await pg.fill("#pin","4321"); await pg.click("[data-t=pin]")
    await pg.evaluate("window.scrollTo(0,document.querySelector('.phone').getBoundingClientRect().top+scrollY-120)"); await pg.wait_for_timeout(2800); await shot("2-client-lk")
    await pg.click("[data-t=to6]"); await pg.wait_for_selector("[data-k]")
    for k in ["ok","4","3","2","1","ok","3","0","0","ok"]: await pg.click(f"[data-k='{k}']")
    await pg.click("[data-k='ok']"); await pg.wait_for_selector("[data-t=to7]",timeout=8000)
    await pg.evaluate("window.scrollTo(0,document.querySelector('.term').getBoundingClientRect().top+scrollY-120)"); await pg.wait_for_timeout(2800); await shot("3-terminal")
    st=await pg.evaluate("window.__demo.state()"); t=st["tx"][0]
    assert t["type"]=="terminal" and t["used"]==90, t
    await pg.click("[data-t=to7]"); await pg.wait_for_timeout(300)
    async with pg.expect_download() as d: await pg.click("[data-t=csv]")
    dl=await d.value; path=OUT+f"{tag}-export.csv"; await dl.save_as(path)
    await pg.click("[data-t=ff]"); await pg.wait_for_timeout(3000)
    await shot("4-partner-cabinet",True)
    st=await pg.evaluate("window.__demo.state()")
    c=list(st["clients"].values())[0]
    print(tag,"partner",st["partner"]["balance"],"client",c["balance"],"spent",c["spent"],"burned",c["burned"],"tx",[x["type"] for x in st["tx"]],"sms",[m["k"] for m in st["sms"]])
    await pg.click("[data-step='8']"); await pg.wait_for_timeout(300)
    await shot("5-platform-admin",True)
    print(tag,"platform comm",await pg.inner_text("[data-t=pcomm]"))
    await pg.click("[data-t=reset]"); await pg.wait_for_timeout(300)
    st=await pg.evaluate("window.__demo.state()"); print(tag,"after reset partner:",st["partner"])
    print(tag,"ERRORS:",errs or "none")
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
        block = "localhost" in BASE
        await flow(b,390,844,"m390",block,["1-purchase-sms","2-client-lk","3-terminal"]); await flow(b,1440,900,"d1440",block,["4-partner-cabinet","5-platform-admin","1-purchase-sms"])
        await b.close()
asyncio.run(main())
