"""Generate descriptive counts, without significance or safety claims."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from handback.analysis import verify, METHODS

ROOT=Path(__file__).resolve().parents[1]
s=verify(ROOT)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'HandBack-0.1.0',
                     'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(10.5,4.2),sharey=True)
for ax,key,title in zip(axes,('joint_2mm','deep_over_5mm'),('Joint success (higher is better)','External depth >5mm (lower is better)')):
    values=[s['counts'][m][key] for m in METHODS]
    colors=['#1b728e' if m=='V' else '#aebcc5' for m in METHODS]
    bars=ax.bar(METHODS,values,color=colors,width=.7)
    ax.set_title(title,loc='left',fontweight='bold',fontsize=11)
    ax.set_ylim(0,12.8);ax.set_yticks([0,2,4,6,8,10,12]);ax.set_axisbelow(True);ax.grid(axis='y',alpha=.2)
    for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,v+.15,str(v)+'/12',ha='center',fontsize=9)
axes[0].set_ylabel('Scene units (one training seed)')
fig.text(.02,.03,'Includes 3 infrastructure re-executions. V and S1 used identical selected data. Contact bounds are simulation screens.',fontsize=8,color='#475569')
fig.subplots_adjust(bottom=.19,left=.07,right=.99,top=.88,wspace=.13)
dest=ROOT/'docs/assets';dest.mkdir(parents=True,exist_ok=True)
fig.savefig(dest/'outcomes.svg',metadata={'Date':None,'Creator':'HandBack figure script'})
svg=dest/'outcomes.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8',newline='\n')
fig.savefig(dest/'outcomes.png',dpi=160,metadata={'Software':'HandBack figure script'})
plt.close(fig)
print('Generated docs/assets/outcomes.svg and outcomes.png')
