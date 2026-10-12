"""Editable lineage diagrams and actual extraction-quality plot for Chapter19."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
plt.rcParams.update({'font.size':14,'svg.fonttype':'none','font.family':'DejaVu Sans'})
BLUE='#005f83'
RED='#a33100'


def box(ax,x,y,w,h,text,face='#edf4f7'):
    ax.add_patch(Rectangle((x,y),w,h,edgecolor=BLUE,facecolor=face,lw=1.5))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=14)


def arrow(ax,a,b,text=None):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.6,'color':'#222'})
    if text:ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.12,text,va='center',fontsize=14,
                    bbox={'facecolor':'white','edgecolor':'none','pad':1})


def save(fig,name):
    svg=HERE/f'{name}.svg'
    fig.savefig(svg,bbox_inches='tight')
    svg.write_bytes(('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n').encode('utf-8'))
    fig.savefig(HERE/f'{name}.png',bbox_inches='tight',dpi=160)
    plt.close(fig)


def lineage():
    fig,ax=plt.subplots(figsize=(10,7.2))
    ax.set(xlim=(0,10),ylim=(-.4,8));ax.axis('off')
    ax.set_title('Figure 19.01 - Publication follows interpretation and validation',pad=18,fontsize=16)
    ax.text(.2,7.45,'INDEX TIME - implemented local corpus stage',color=BLUE,weight='bold')
    box(ax,1,6.45,4,.65,'Source descriptors\nidentity + policy')
    ax.add_patch(Polygon([[3,6.15],[4.4,5.5],[3,4.85],[1.6,5.5]],facecolor='#fff8eb',edgecolor=BLUE))
    ax.text(3,5.5,'Scope + use\napproved?',ha='center',va='center')
    arrow(ax,(3,6.45),(3,6.15))
    box(ax,6.5,5.15,3,.7,'Policy block\nNo source read')
    arrow(ax,(4.4,5.5),(6.5,5.5),'no')
    box(ax,1,3.9,4,.65,'Capture bytes\n+ source checksum')
    arrow(ax,(3,4.85),(3,4.55))
    ax.text(3.2,4.68,'yes')
    box(ax,1,2.85,4,.65,'Parse ordered units\n+ source anchors')
    arrow(ax,(3,3.9),(3,3.5))
    box(ax,1,1.8,4,.65,'Normalize / validate\n+ group duplicate aliases')
    arrow(ax,(3,2.85),(3,2.45))
    box(ax,6.5,2.5,3,.85,'Quality quarantine\nReview / repair',face='#fff1e9')
    arrow(ax,(5,3.15),(6.5,3.15),'fail')
    arrow(ax,(5,2.1),(6.5,2.5))
    box(ax,1,.7,4,.7,'Publish canonical record\n+ source lineage')
    arrow(ax,(3,1.8),(3,1.4))
    box(ax,6.5,.7,3,.7,'Later: chunk\nembed / index')
    arrow(ax,(5,1.05),(6.5,1.05))
    ax.text(.2,-.15,'Rectangles: actions/stores; diamond: policy gate. Query retrieval is downstream.',fontsize=14)
    save(fig,'figure-19-01-lineage')


def span():
    docs=json.loads((ROOT/'projects/V5/canonical_ch19/structured.json').read_text(encoding='utf-8'))
    doc=next(d for d in docs if d['source_id']=='S-pdf')
    block=doc['blocks'][1];loc=block['locator']
    fig,ax=plt.subplots(figsize=(10,5.7))
    ax.set(xlim=(0,10),ylim=(0,6));ax.axis('off')
    ax.set_title('Figure 19.02 - A canonical span resolves to a pinned page region',pad=16,fontsize=16)
    box(ax,.2,3.55,4.1,1.5,f"CANONICAL BODY\n{block['block_id']} [{block['start']},{block['end']})\nFirst response is four hours.")
    box(ax,.2,1.65,4.1,1.25,'Pinned source identity\nParser / normalization identity\nCanonical record digest')
    arrow(ax,(2.25,3.55),(2.25,2.9))
    ax.add_patch(Rectangle((6.2,1.4),3,3.88,facecolor='white',edgecolor='#333',lw=1.5))
    x0,y0,x1,y1=loc['bbox'];scale=3/612
    ax.add_patch(Rectangle((6.2+x0*scale,5.28-y1*scale),(x1-x0)*scale,(y1-y0)*scale,
                          facecolor='#cbe5f0',edgecolor=BLUE,lw=2))
    ax.text(7.7,5.55,'Pinned original: page 1',ha='center',fontsize=14)
    arrow(ax,(4.3,2.3),(6.2+x0*scale,5.28-(y0+y1)/2*scale))
    ax.text(7.7,1.05,'Schematic page; actual box',ha='center',fontsize=14)
    ax.text(.3,.65,f"bbox = [{x0:.2f}, {y0:.2f}, {x1:.2f}, {y1:.2f}] points",fontsize=14)
    ax.text(.3,.2,'Unrotated PyMuPDF top-left coordinates; whole block, not inverse raw offsets.',fontsize=14)
    save(fig,'figure-19-02-span')


def quality():
    record=json.loads((ROOT/'projects/V5/chapter-19-experiment.json').read_text(encoding='utf-8'))
    fig,ax=plt.subplots(figsize=(9.5,5.6))
    modes=['flat','structured'];keys=['preservation_rate','traceable_preservation_rate','source_hit_at_1']
    labels=['Required span\npreserved','Preserved +\nsource-region traced','Lexical source\nHit@1']
    for j,mode in enumerate(modes):
        values=[record['summaries'][mode][k] for k in keys]
        bars=ax.bar([i+(j-.5)*.34 for i in range(3)],values,.32,label=mode.capitalize(),color=[RED,BLUE][j])
        for bar,value in zip(bars,values):
            ax.text(bar.get_x()+bar.get_width()/2,value+.025,f'{round(value*8)}/8',ha='center',fontsize=14)
    ax.set_xticks(range(3),labels);ax.set_ylim(0,1.12)
    ax.set_ylabel('Fraction of eight inspected requirements')
    ax.set_title('Figure 19.03 - Source discovery and preserved evidence differ',fontsize=16,pad=16)
    ax.legend(loc='upper right',fontsize=14)
    ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.subplots_adjust(bottom=.28)
    fig.text(.5,.10,'ch19-source-quality-v1 - authored / inspected probes, no held-out split or CI',ha='center',fontsize=14)
    fig.text(.5,.045,'Scan remains quarantined; source hits do not measure evidence or answers.',ha='center',fontsize=14)
    save(fig,'figure-19-03-quality')


if __name__=='__main__':
    lineage();span();quality()
