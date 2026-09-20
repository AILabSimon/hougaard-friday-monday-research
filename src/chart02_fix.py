import sys, os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR","/tmp/mpl")
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT
from stats_util import newcombe_diff
T = pd.read_parquet(DERIVED/"triples"/"triples_duka.parquet")
T["grp"] = np.where(T.instrument.isin(["NAS100","US500"]),"US equity indices",
            np.where(T.asset_class=="FX","FX majors",
            np.where(T.instrument=="BTCUSD","crypto","metals / energy")))
def logit_fit(X,y,ridge=1e-4,iters=200):
    X=np.asarray(X,float);y=np.asarray(y,float);b=np.zeros(X.shape[1])
    for _ in range(iters):
        eta=X@b;p=1/(1+np.exp(-np.clip(eta,-30,30)));W=np.clip(p*(1-p),1e-8,None)
        H=X.T@(X*W[:,None])+ridge*np.eye(X.shape[1]);g=X.T@(y-p)-ridge*b
        s=np.linalg.solve(H,g);b=b+s
        if np.max(np.abs(s))<1e-9:break
    eta=X@b;p=1/(1+np.exp(-np.clip(eta,-30,30)));W=np.clip(p*(1-p),1e-8,None)
    return b,np.sqrt(np.diag(np.linalg.inv(X.T@(X*W[:,None])+ridge*np.eye(X.shape[1]))))
rows=[]
for sdef in ["BROKER"]:
    for wd in range(5):
        for grp,g in T[(T.sessdef==sdef)&(T.B_wd==wd)].groupby("grp"):
            if grp=="crypto": continue
            t,o=g[g.trig_down],g[~g.trig_down]
            lo,hi=newcombe_diff(int(t.touch_low.sum()),len(t),int(o.touch_low.sum()),len(o))
            d=g.dropna(subset=["atr_at_B"]); d=d[d.B_range>0]
            X=np.column_stack([np.ones(len(d)),d.trig_down.astype(float),
                               (d.B_close-d.B_low)/d.atr_at_B, d.B_range/d.atr_at_B])
            for i in sorted(d.instrument.unique())[1:]:
                X=np.column_stack([X,(d.instrument==i).astype(float)])
            b,se=logit_fit(X,d.touch_low.values.astype(float))
            rows.append(dict(wd=["Mon","Tue","Wed","Thu","Fri"][wd],grp=grp,
                             raw=t.touch_low.mean()-o.touch_low.mean(),raw_lo=lo,raw_hi=hi,
                             beta=b[1],se=se[1]))
D=pd.DataFrame(rows); order=["Mon","Tue","Wed","Thu","Fri"]
COL={"US equity indices":"#c0392b","FX majors":"#2980b9","metals / energy":"#27ae60"}
plt.rcParams.update({"figure.dpi":130,"font.size":9,"axes.grid":True,"grid.alpha":.3,
                     "axes.spines.top":False,"axes.spines.right":False})
fig,axes=plt.subplots(1,2,figsize=(11.5,4.2))
for grp,g in D.groupby("grp"):
    g=g.set_index("wd").reindex(order); x=np.arange(5)
    off={"US equity indices":-.08,"FX majors":0,"metals / energy":.08}[grp]
    axes[0].errorbar(x+off,g.raw,yerr=[g.raw-g.raw_lo,g.raw_hi-g.raw],marker="o",capsize=3,
                     color=COL[grp],label=grp,lw=1.6)
    axes[1].errorbar(x+off,g.beta,yerr=1.96*g.se,marker="o",capsize=3,color=COL[grp],label=grp,lw=1.6)
for ax,t_ in zip(axes,["RAW: uplift vs the opposite condition",
                       "AFTER controlling for where the bar closed in its range"]):
    ax.axhline(0,c="k",lw=1); ax.set_xticks(np.arange(5)); ax.set_xticklabels(order); ax.set_title(t_,fontsize=10)
axes[0].set_ylabel("Δ P(next session takes this session's low)")
axes[1].set_ylabel("logistic β on the trigger")
axes[0].set_xlabel("day whose high failed  (Fri → Mon is the Hougaard case)")
axes[1].set_xlabel("day whose high failed  (Fri → Mon is the Hougaard case)")
axes[1].legend(fontsize=8,loc="upper left")
fig.suptitle("The raw effect exists on every weekday pair. After the control only US equity indices retain one — largest on Friday.",y=1.02,fontsize=11)
fig.tight_layout(); fig.savefig(OUT/"charts"/"02_adjacent_weekday.png",bbox_inches="tight")
print(D.to_string(index=False,float_format=lambda x:f"{x:.3f}"))
