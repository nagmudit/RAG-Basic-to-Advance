"""Actual canonical boundaries and measured chunk/packing outcomes."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'svg.fonttype':'none'})
BLUE='#005f83';RED='#a33100';GRAY='#64737b'


def save(fig,name):
    path=HERE/f'{name}.svg';fig.savefig(path,bbox_inches='tight')
    path.write_bytes(('\n'.join(x.rstrip() for x in path.read_text(encoding='utf-8').splitlines())+'\n').encode('utf-8'))
    fig.savefig(HERE/f'{name}.png',bbox_inches='tight',dpi=160);plt.close(fig)


def box(ax,x,y,w,h,text):
    ax.add_patch(Rectangle((x,y),w,h,facecolor='#edf4f7',edgecolor=BLUE,lw=1.4))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=14)


def arrow(ax,a,b):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.5,'color':'#222'})


def boundaries(index,labels):
    fig,ax=plt.subplots(figsize=(10.5,5.7))
    modes=['char128','word24','word24-o8','structure48']
    req=next(q for q in labels['queries'] if q['query_id']=='blue-wait')['requirements'][0]
    a,z=req['canonical_span'];ax.axvspan(a,z,color=RED,alpha=.13,label='Required waiting-period span')
    for i,mode in enumerate(modes):
        rows=[r for r in index['indexes'][mode]['rows'] if r['source_id']=='S-ops']
        for j,r in enumerate(rows):
            x,y=r['canonical_span']
            if x<750:
                ax.broken_barh([(x,min(y,750)-x)],(i-.22,.44),facecolors=BLUE if j%2==0 else GRAY,alpha=.7,edgecolors='white')
    ax.set(xlim=(0,750),ylim=(-.6,3.6),yticks=range(4),yticklabels=modes)
    ax.invert_yaxis();ax.set_xlabel('Canonical code-point offset in S-ops (first 750 only)')
    ax.set_title('Figure 20.01 - The same source, competing boundaries',fontsize=16,pad=18)
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    fig.subplots_adjust(bottom=.30)
    fig.text(.5,.145,'Shaded region: required waiting-period span',ha='center',fontsize=14,color=RED)
    fig.text(.5,.08,'Actual ranges; darker overlap repeats positions. Placement does not prove a hit.',ha='center',fontsize=14)
    fig.text(.5,.025,'ch20-chunked-evidence-v1 - pinned source/record and independent required span',ha='center',fontsize=14)
    save(fig,'figure-20-01-boundaries')


def expansion():
    fig,ax=plt.subplots(figsize=(10.5,5.8));ax.set(xlim=(0,10),ylim=(0,6));ax.axis('off')
    ax.set_title('Figure 20.02 - Matching and expansion have different budgets',fontsize=16,pad=18)
    ax.text(.2,5.45,'QUERY TIME - word24-parent; child index unchanged',color=BLUE,weight='bold')
    box(ax,.2,3.9,2.7,1,'Eligible top-3\nchild matches')
    box(ax,3.55,3.9,2.7,1,'Source / version /\nscope / use check')
    box(ax,6.9,3.9,2.7,1,'Resolve full parent\nS-ops: 517 WP')
    arrow(ax,(2.9,4.4),(3.55,4.4));arrow(ax,(6.25,4.4),(6.9,4.4))
    ax.add_patch(Polygon([[8.25,3.5],[9.5,2.7],[8.25,1.9],[7,2.7]],facecolor='#fff8eb',edgecolor=BLUE))
    ax.text(8.25,2.7,'Fit 80\nWordPieces?',ha='center',va='center')
    arrow(ax,(8.25,3.9),(8.25,3.5))
    box(ax,6.9,.6,2.7,.9,'Budget rejection\nNo selected parent')
    arrow(ax,(8.25,1.9),(8.25,1.5));ax.text(8.5,1.63,'no')
    box(ax,.2,.9,3.4,1,'Smaller verified parents\nmay fit and be selected')
    ax.text(.2,3.05,'Several children can cause one parent attempt.',fontsize=14)
    ax.text(.2,2.65,'Retain child causes and duplicate/budget reasons.',fontsize=14)
    ax.text(.2,.15,'Actual whole-parent rejection; WP counts are an encoder-budget proxy, not generator tokens.',fontsize=14)
    save(fig,'figure-20-02-expansion')


def mechanisms():
    fig,ax=plt.subplots(figsize=(10.5,6.3));ax.set(xlim=(0,10),ylim=(0,6.5));ax.axis('off')
    ax.set_title('Figure 20.03 - Context enters at different stages',fontsize=16,pad=18)
    rows=[(4.8,['QUERY TIME\nchild match','Verify / expand\noriginal parent','Budget / select\nreading context']),
          (2.85,['INDEX TIME\nchunk + description','Independent\nchunk encoding','Store prefixed\nchunk vector']),
          (.9,['INDEX TIME\nlong source','Contextual\ntoken states','Chunk-boundary\npooling -> vectors'])]
    for y,texts in rows:
        for x,t in zip([.2,3.65,7.1],texts):box(ax,x,y,2.7,1,t)
        arrow(ax,(2.9,y+.5),(3.65,y+.5));arrow(ax,(6.35,y+.5),(7.1,y+.5))
    ax.text(.2,4.4,'Parent expansion: executed in the bounded experiment',fontsize=14)
    ax.text(.2,2.45,'Contextual description/prefix: conceptual, not run',fontsize=14)
    ax.text(.2,.5,'Late chunking: conceptual; needs suitable long-context token states',fontsize=14)
    save(fig,'figure-20-03-context-mechanisms')


def quality(record):
    modes=list(record['summaries']);labels=['char\n128','word\n24','word24\nO8','word\n48','word\n96','struct\n48','child\nparent']
    fig,(ax,bx)=plt.subplots(2,1,figsize=(10.5,7.4),sharex=True,gridspec_kw={'height_ratios':[2.2,1]})
    for j,(key,color,name) in enumerate([('candidate_evidence_recall_at_3',BLUE,'Candidate Recall@3'),('context_evidence_recall',RED,'Packed context recall')]):
        ax.bar([i+(j-.5)*.34 for i in range(len(modes))],[record['summaries'][m][key] for m in modes],.32,color=color,label=name)
    ax.set_ylim(0,1.13);ax.set_ylabel('Macro atom recall (10 positives)')
    ax.legend(fontsize=14,loc='upper left',bbox_to_anchor=(0,1.16),ncol=2,borderaxespad=0)
    ax.set_title('Figure 20.04 - Candidate coverage and selected evidence diverge',fontsize=16,pad=58)
    bx.bar(range(len(modes)),[record['summaries'][m]['mean_context_duplicate_source_fraction'] for m in modes],color=GRAY,width=.55)
    bx.set_ylim(0,.115);bx.set_ylabel('Mean duplicate\nsource fraction');bx.set_xticks(range(len(modes)),labels)
    for a in [ax,bx]:a.grid(axis='y',alpha=.15);a.set_axisbelow(True)
    fig.subplots_adjust(bottom=.23,hspace=.18,top=.80)
    fig.text(.5,.085,'ch20-chunked-evidence-v1 - k3; whole-unit budget80 encoder WordPieces; no CI',ha='center',fontsize=14)
    fig.text(.5,.035,'Duplicate mean: all 12 questions. Categorical policies; no answer/generation metric.',ha='center',fontsize=14)
    save(fig,'figure-20-04-quality')


if __name__=='__main__':
    index=json.loads((ROOT/'projects/V5/index_ch20/index.json').read_text(encoding='utf-8'))
    labels=json.loads((ROOT/'projects/V5/evidence_spans_ch20.json').read_text(encoding='utf-8'))
    record=json.loads((ROOT/'projects/V5/chapter-20-experiment.json').read_text(encoding='utf-8'))
    boundaries(index,labels);expansion();mechanisms();quality(record)
