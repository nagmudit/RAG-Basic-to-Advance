"""Exact query/route diagrams and the checked matched-workload quality plot."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Polygon

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
plt.rcParams.update({'font.size':16,'svg.fonttype':'none','font.family':'DejaVu Sans'})
BLUE,ORANGE,GREEN,INK='#245a81','#a95418','#27715b','#172c3c'


def save(fig,name):
    fig.savefig(HERE/(name+'.svg'),bbox_inches='tight')
    fig.savefig(HERE/(name+'.png'),dpi=160,bbox_inches='tight')
    p=HERE/(name+'.svg');p.write_bytes(('\n'.join(s.rstrip() for s in p.read_text('utf-8').splitlines())+'\n').encode())
    plt.close(fig)


def canvas(h):
    fig,ax=plt.subplots(figsize=(11,h));ax.set(xlim=(0,11),ylim=(0,h));ax.axis('off');return fig,ax


def box(ax,x,y,text,w=2.6,h=.85,gate=False,color=BLUE):
    shape=Polygon([(x,y+h/2),(x+w/2,y+h),(x+w,y+h/2),(x+w/2,y)],facecolor='#f4f7fa',edgecolor=color,linewidth=1.8) if gate else FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.025,rounding_size=.05',facecolor='#f4f7fa',edgecolor=color,linewidth=1.8)
    ax.add_patch(shape);ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=16,color=INK)


def arrow(ax,a,b,label=None,dashed=False):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','linewidth':1.7,'color':INK,'linestyle':'--' if dashed else '-'})
    if label:ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.12,label,ha='center',fontsize=16)


fig,ax=canvas(5.3)
ax.text(.2,5.02,'QUERY TIME — preserved original, explicit representation jobs',weight='bold')
box(ax,.2,3.8,'Original text\nretained',w=2.5)
box(ax,3.6,3.8,'NFC + whitespace\nsurface',w=3)
arrow(ax,(2.7,4.2),(3.6,4.2))
box(ax,3.6,2.05,'Interpret cues\n+ prior slot',w=3)
arrow(ax,(5.1,3.8),(5.1,2.9))
box(ax,7.8,3.8,'Surface → query\nembedding',w=3)
arrow(ax,(6.6,4.2),(7.8,4.2))
box(ax,7.8,2.05,'Locked ID field\n+ surface terms',w=3)
arrow(ax,(6.6,2.48),(7.8,2.48))
box(ax,.2,.6,'Trusted principal\nsupplied separately',w=3)
box(ax,5.0,.6,'Typed task + current authority\nbefore body/vector scoring',w=5.7)
arrow(ax,(3.2,1.03),(5,1.03));arrow(ax,(5.1,2.05),(6.4,1.45))
ax.text(.2,.1,'Cue casefolding does not replace exact ID case. No generated rewrite.',fontsize=16)
save(fig,'figure-23-01-representations')

fig,ax=canvas(7.5)
ax.text(.2,7.12,'QUERY TIME — closed grammar and local capability registry',weight='bold')
box(ax,.3,5.8,'Ambiguous?',w=2.8,h=1.0,gate=True)
box(ax,7.3,5.87,'Clarify / no search',w=3.3,color=ORANGE)
arrow(ax,(3.1,6.3),(7.3,6.3),'yes')
box(ax,.3,4.4,'English hint?',w=2.8,h=1,gate=True)
arrow(ax,(1.7,5.8),(1.7,5.4));ax.text(1.9,5.58,'no ambiguity')
box(ax,7.3,4.45,'Unsupported\nlanguage',w=3.3,color=ORANGE)
arrow(ax,(3.1,4.9),(7.3,4.9),'no')
arrow(ax,(1.7,4.4),(1.7,3.95))
ax.text(.35,3.65,'Operation',weight='bold');ax.text(3.75,3.65,'Primary',weight='bold');ax.text(7.15,3.65,'Local outcome',weight='bold')
rows=[('Exact ID','Lexical','Ready lexical'),('Paraphrase / date','Dense','Ready dense'),('Count / fresh public','SQL / web','Unsupported'),('Relationship','Graph','Partial lexical evidence')]
for i,(kind,primary,result) in enumerate(rows):
    y=3.14-i*.55;ax.text(.35,y,kind);ax.text(3.75,y,primary);ax.text(7.15,y,result,color=ORANGE if i>=2 else BLUE)
    ax.plot([.3,10.7],[y-.12,y-.12],color='#ccd7e0',linewidth=.8)
box(ax,.4,.02,'Available retrieval → current grants / source version → scoring',w=10.2,h=.70)
ax.text(.3,.97,'Registry: lexical + dense. Other backends do not execute.',fontsize=16)
save(fig,'figure-23-02-decision')

fig,ax=canvas(6.0)
ax.text(.2,5.65,'QUERY TIME — ch23-bounded-route-fallback-v1',weight='bold')
box(ax,.2,4.25,'Parent plan\nfixed constraints',w=2.6)
box(ax,3.8,4.13,'Task empty?',w=2.6,h=1.1,gate=True)
box(ax,8.0,4.25,'Terminal empty\nzero attempts',w=2.8,color=ORANGE)
arrow(ax,(2.8,4.68),(3.8,4.68));arrow(ax,(6.4,4.68),(8,4.68),'yes')
box(ax,3.8,2.62,'Attempt 1\nlexical or dense',w=2.6)
arrow(ax,(5.1,4.13),(5.1,3.47));ax.text(5.3,3.72,'no')
box(ax,8.0,2.62,'Attempt 2\ncompatible route',w=2.8)
arrow(ax,(6.4,3.05),(8,3.05),'timeout')
box(ax,.2,1.0,'Actual candidates\n→ context packing',w=3)
arrow(ax,(3.8,3.05),(1.7,1.85));ax.text(.4,2.35,'completed')
arrow(ax,(8,2.62),(3.2,1.85));ax.text(5.7,2.12,'completed')
box(ax,8.0,1.0,'Both timeout\nstop at budget 2',w=2.8,color=ORANGE)
arrow(ax,(9.4,2.62),(9.4,1.85))
ax.text(.2,.33,'Child IDs link to parent. No hard-constraint widening or score fusion.',fontsize=16)
ax.text(.2,.0,'Timeouts are immediate injected exceptions, not measured deadlines.',fontsize=16)
save(fig,'figure-23-03-fallback')

record=json.loads((ROOT/'projects/V7/chapter-23-experiment.json').read_text('utf-8'))
fig,ax=plt.subplots(figsize=(11,6.2))
modes=['dense_all','constraint_dense','rule_route'];x=range(3);width=.32
values=[record['aggregates'][m]['positive_recall_at_2'] for m in modes]
context=[record['aggregates'][m]['context_evidence_recall'] for m in modes]
for offset,vals,color,label,hatch in ((-width/2,values,BLUE,'Candidate Recall@2 (10 positives)',None),(width/2,context,ORANGE,'Context evidence recall (10 positives)','///')):
    bars=ax.bar([v+offset for v in x],vals,width,color=color,label=label,hatch=hatch)
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.025,f'{v:.3f}',ha='center',fontsize=16)
ax.set(ylim=(0,1.08),ylabel='Macro recall (fraction)',xticks=list(x),xticklabels=['All dense','Interpreted\ndense','Rule\nrouting'])
ax.set_title('ch23-query-plans-v1 — interpretation versus route choice',fontsize=16)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),frameon=False,fontsize=16)
fig.subplots_adjust(left=.1,right=.98,top=.89,bottom=.40)
fig.text(.12,.085,'Both interpreted policies miss the answerable quantity query.',fontsize=16)
fig.text(.12,.035,'Publication pair: 68 WordPieces ≤ budget 80. Three repeats; no independent CI.',fontsize=16)
save(fig,'figure-23-04-quality')
