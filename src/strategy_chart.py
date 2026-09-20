import sys, os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR","/tmp/mpl")
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT
CH = OUT/"charts"
G = pd.read_parquet(DERIVED/"monday_grid.parquet")
P = pd.read_parquet(DERIVED/"monday_paths.parquet")
for d in (G,P):
    d["grp"] = np.where(d.instrument.isin(["NAS100","US500"]),"US_INDEX","FX")
col = lambda k: f"t{k:+.2f}"

rows=[]
for (sdef,grp),g in G.groupby(["sessdef","grp"]):
    for trig in (True,False):
        gg=g[g.trig_down==trig]
        for sk,tk in [(0.5,0.5),(0.5,1.0),(0.5,1.5),(0.75,1.5),(1.0,1.0),(1.0,2.0)]:
            ts=gg[col(-tk)].values; tl=gg[col(sk)].values
            win=~np.isnan(ts)&(np.isnan(tl)|(ts<tl)); loss=~np.isnan(tl)&(np.isnan(ts)|(tl<ts))
            mtm=(gg.C_open_px.values-gg.C_close.values)/(sk*gg.atr_at_B.values)
            R=np.where(win,tk/sk,np.where(loss,-1.0,mtm))
            rows.append(dict(sessdef=sdef,grp=grp,trig=trig,cons=f"{sk}/{tk} ATR ({tk/sk:.0f}R)",
                             n=len(gg),win=win.mean(),meanR=np.nanmean(R)))
D=pd.DataFrame(rows); D.to_csv(OUT/"strategy_expectancy.csv",index=False)

fig,axes=plt.subplots(1,2,figsize=(11,3.8),sharey=True)
for ax,grp in zip(axes,["US_INDEX","FX"]):
    d=D[(D.grp==grp)&(D.sessdef=="RTH")]
    cons=d.cons.unique(); x=np.arange(len(cons)); w=.35
    ax.bar(x-w/2,d[d.trig].set_index("cons").reindex(cons).meanR,w,label="triggered (Fri high < Thu high)",color="#c0392b")
    ax.bar(x+w/2,d[~d.trig].set_index("cons").reindex(cons).meanR,w,label="not triggered",color="#9aa5b1")
    ax.axhline(0,c="k",lw=.9); ax.set_xticks(x); ax.set_xticklabels(cons,rotation=25,fontsize=7.5)
    ax.set_title(f"{grp} — short at Monday RTH open")
axes[0].set_ylabel("mean R per trade (before costs)"); axes[0].legend(fontsize=7.5)
fig.suptitle("Every fixed-R short construction loses money, triggered or not",y=1.03)
fig.tight_layout(); fig.savefig(CH/"07_strategy_expectancy.png",bbox_inches="tight"); plt.close(fig)

# R available at Friday's close
fig,ax=plt.subplots(figsize=(7,3.6))
p=P[(P.sessdef=="RTH")&(P.grp=="US_INDEX")].copy()
p["Rt"]=(p.B_close-p.B_low)/(p.B_high-p.B_close).replace(0,np.nan)
for trig,c,l in [(True,"#c0392b","triggered"),(False,"#9aa5b1","not triggered")]:
    ax.hist(np.clip(p[p.trig_down==trig].Rt,0,6),bins=40,histtype="step",density=True,lw=1.5,color=c,label=l)
ax.axvline(1,ls=":",c="k"); ax.set_xlabel("reward:risk available at Friday's close  (Fri close→Fri low) / (Fri high→Fri close)")
ax.set_title("The trigger selects the setups with the WORST payoff geometry"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(CH/"08_payoff_geometry.png",bbox_inches="tight"); plt.close(fig)
print(D[(D.grp=="US_INDEX")].to_string(index=False,float_format=lambda x:f"{x:.3f}"))
