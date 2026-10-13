"""Source-clock, replay, migration and matched-quality figures from checked data."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Polygon

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
record=json.loads((ROOT/'projects/V6/chapter-22-experiment.json').read_text('utf-8'))
plt.rcParams.update({'font.size':16,'svg.fonttype':'none','font.family':'DejaVu Sans'})
BLUE,ORANGE,GREEN,INK='#245a81','#a95418','#27715b','#172c3c'


def save(fig,name):
    fig.savefig(HERE/(name+'.svg'),bbox_inches='tight');fig.savefig(HERE/(name+'.png'),dpi=160,bbox_inches='tight')
    p=HERE/(name+'.svg');p.write_bytes(('\n'.join(s.rstrip() for s in p.read_text('utf-8').splitlines())+'\n').encode('utf-8'));plt.close(fig)


def canvas(height=6):
    fig,ax=plt.subplots(figsize=(11,height));ax.set(xlim=(0,11),ylim=(0,height));ax.axis('off');return fig,ax


def box(ax,x,y,text,w=2.4,h=1,gate=False,color=BLUE):
    if gate:patch=Polygon([(x,y+h/2),(x+w/2,y+h),(x+w,y+h/2),(x+w/2,y)],facecolor='#f4f7fa',edgecolor=color,linewidth=1.8)
    else:patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.03,rounding_size=.07',facecolor='#f4f7fa',edgecolor=color,linewidth=1.8)
    ax.add_patch(patch);ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=16,color=INK)


def arrow(ax,x1,y1,x2,y2,dashed=False):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops={'arrowstyle':'->','linewidth':1.6,'color':INK,'linestyle':'--' if dashed else '-'})


fig,ax=plt.subplots(figsize=(11,5.8))
labels=['A06 edit v2','A03 delete v2','A08 grant change v2','A06 edit v3'];starts=[1000,2000,3000,4000];ends=[1200,2600,3900,4500]
for i,(a,b) in enumerate(zip(starts,ends)):
    ax.plot([a,b],[i,i],color=BLUE,linewidth=4);ax.scatter(a,i,color=ORANGE,s=100,marker='s');ax.scatter(b,i,color=GREEN,s=100)
    ax.text((a+b)/2,i-.2,f'{b-a} ms',ha='center',fontsize=16)
ax.axvline(4200,color=INK,linestyle=':',linewidth=1.5)
ax.text(4130,.2,'Question at 4200:\nv3 known, not visible',ha='right',fontsize=16)
ax.set(yticks=range(4),yticklabels=labels,xlim=(500,5300),ylim=(-.5,3.6),xlabel='Controlled logical time (milliseconds)',title='ch22-controlled-event-delivery-v1 — scheduled visibility gaps')
ax.invert_yaxis();ax.scatter([],[],color=ORANGE,marker='s',label='Source effective/commit position');ax.scatter([],[],color=GREEN,label='Projection published position')
fig.legend(loc='lower center',bbox_to_anchor=(.6,.06),frameon=False,fontsize=16)
fig.text(.05,.015,'Prepared vectors; logical gaps are not measured service or worker latency.',fontsize=16)
fig.subplots_adjust(left=.25,bottom=.32,right=.98,top=.88)
save(fig,'figure-22-01-clocks')

fig,ax=canvas(6.6)
ax.text(.1,6.1,'Same deliveries; different source heads',weight='bold')
for y,label,a,b in ((4.65,'ORDERED','A03: delete v2','A06: live v3'),(3.0,'LAST ARRIVAL','A03: live v1','A06: live v1')):
    ax.text(.1,y+.4,label,weight='bold',fontsize=16)
    box(ax,3,y,a,w=3,h=1.05);box(ax,7,y,b,w=3,h=1.05,color=GREEN if label=='ORDERED' else ORANGE)
box(ax,.6,.7,'Current\npolicy\ngate',w=2.7,h=1.2,gate=True)
box(ax,4.1,.7,'Known\nrevision\nbarrier',w=2.9,h=1.2,gate=True)
box(ax,8,.7,'Context:\nintended\nevidence',w=2.7,h=1.2)
arrow(ax,3.3,1.3,4.1,1.3);arrow(ax,7,1.3,8,1.3)
ax.text(.4,2.2,'A03 denied before scoring; permitted obsolete A06 scored then excluded.',fontsize=16)
ax.text(.1,.12,'Head state is privileged audit data; no deleted/private ID enters reader candidates.',fontsize=16)
save(fig,'figure-22-02-replay')

fig,ax=canvas(7)
ax.text(.1,6.55,'INDEX / CONTROL TIME — two input contracts, one frozen backbone',weight='bold')
box(ax,.2,4.95,'Old/body\nserving index',w=2.6)
box(ax,4,4.95,'Source updates\n+ retained tail',w=2.8)
box(ax,8.3,4.95,'New/entity-body\nbackfill at 3500',w=2.5)
arrow(ax,4,5.45,2.8,5.45);arrow(ax,6.8,5.45,8.3,5.45)
box(ax,7.9,3.3,'Catch up tail\n3900 ... 5200',w=2.9)
arrow(ax,9.5,4.95,9.35,4.3)
box(ax,4.25,3.1,'Head/history\ncoverage\ngate',w=3.0,h=1.3,gate=True)
arrow(ax,7.9,3.8,7.25,3.75)
box(ax,.2,3.3,'Untailed target:\ncutover rejected',w=3.1,color=ORANGE)
arrow(ax,4.25,3.75,3.3,3.8)
box(ax,4.25,1.25,'Validated pointer\nflip to new',w=3.0,h=1.05,color=GREEN)
arrow(ax,5.75,3.1,5.75,2.3)
box(ax,.2,1.25,'Rollback: old\nkept current',w=3.1,h=1.05)
arrow(ax,4.25,1.8,3.3,1.8,True)
box(ax,8,1.25,'QUERY TIME:\nmatching contract',w=2.8,h=1.05)
arrow(ax,7.25,1.8,8,1.8)
ax.text(.1,.35,'Solid = changes/control; dashed = validated rollback. Equal dimension is insufficient.',fontsize=16)
save(fig,'figure-22-03-migration')

fig,ax=plt.subplots(figsize=(11,6))
values=[record['aggregates'][m]['macro_recall_at_1'] for m in ('arrival','ordered')]
context=[record['aggregates'][m]['macro_context_evidence_recall'] for m in ('arrival','ordered')]
b1=ax.bar([-.19,.81],values,width=.36,color=BLUE,label='Candidate Recall@1 (6 positives)')
b2=ax.bar([.19,1.19],context,width=.36,color=ORANGE,hatch='//',label='Context evidence recall (6 positives)')
ax.bar_label(b1,fmt='%.3f',padding=4,fontsize=16);ax.bar_label(b2,fmt='%.3f',padding=4,fontsize=16)
ax.set(xticks=[0,1],xticklabels=['Last arrival','Revision ordered'],ylim=(0,1.02),ylabel='Macro recall (fraction)',title='ch22-versioned-evidence-v1 — source-version evidence')
fig.legend(loc='lower center',bbox_to_anchor=(.5,.16),frameon=False,fontsize=16)
fig.text(.12,.005,'Known-pending: both miss at 4200 (source 4000; publication 4500).\nFour empty tasks are correct in both; three repeats.\nNo independent confidence interval.',fontsize=16)
fig.subplots_adjust(bottom=.35,top=.87,left=.10,right=.98)
save(fig,'figure-22-04-quality')
