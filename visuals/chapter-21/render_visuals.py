"""Exact diagrams and measured categorical plot; run from repository root."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
record = json.loads((ROOT/'projects/V6/chapter-21-experiment.json').read_text('utf-8'))
plt.rcParams.update({'font.size': 16, 'svg.fonttype': 'none', 'font.family': 'DejaVu Sans'})
BLUE, ORANGE, GREEN, INK = '#245a81', '#ae5c1c', '#27715b', '#172c3c'


def canvas(height=6):
    fig, ax = plt.subplots(figsize=(11, height))
    ax.set(xlim=(0, 11), ylim=(0, height))
    ax.axis('off')
    return fig, ax


def box(ax, x, y, label, width=1.9, height=1, gate=False, color=BLUE):
    if gate:
        patch = Polygon([(x, y+height/2), (x+width/2, y+height), (x+width, y+height/2), (x+width/2, y)],
                        facecolor='#f4f7fa', edgecolor=color, linewidth=1.8)
    else:
        patch = FancyBboxPatch((x, y), width, height, boxstyle='round,pad=0.03,rounding_size=0.07',
                              facecolor='#f4f7fa', edgecolor=color, linewidth=1.8)
    ax.add_patch(patch)
    ax.text(x+width/2, y+height/2, label, ha='center', va='center', color=INK, fontsize=16)


def arrow(ax, x1, y1, x2, y2, dashed=False):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops={'arrowstyle': '->', 'color': INK,
                'linewidth': 1.6, 'linestyle': '--' if dashed else '-'})


def save(fig, name, layout=True):
    if layout:
        fig.tight_layout(pad=1)
    fig.savefig(HERE/(name+'.svg'), bbox_inches='tight')
    fig.savefig(HERE/(name+'.png'), dpi=160, bbox_inches='tight')
    path = HERE/(name+'.svg')
    path.write_bytes(('\n'.join(line.rstrip() for line in path.read_text('utf-8').splitlines())+'\n').encode('utf-8'))
    plt.close(fig)


fig, ax = canvas(6.5)
ax.text(.1, 6.1, 'INDEX TIME — content and governed fields keep their identities', weight='bold')
for x, text, gate in ((.1, 'Policy / use\ngate', True), (2.9, 'Parse source\n+ anchors', False),
                      (5.7, 'Chunk + attach\nmetadata digest', False), (8.5, 'Checked store:\nvectors + fields', False)):
    box(ax, x, 4.55, text, width=2.2, height=1.1, gate=gate)
for x in (.1, 2.9, 5.7): arrow(ax, x+2.2, 5.1, x+2.8, 5.1)
ax.text(.1, 3.9, 'QUERY TIME — authority comes from trusted identity context', weight='bold')
labels = ['Trusted\nprincipal', 'Authorized\nview A', 'Task subset\nA \u2229 F', 'Score +\nfinal top-k', 'Recheck +\ncontext fetch']
for n, label in enumerate(labels):
    box(ax, .1+2.2*n, 2.3, label, gate=n==1, height=1.2)
for n in range(4): arrow(ax, 2+2.2*n, 2.9, 2.3+2.2*n, 2.9)
arrow(ax, 9.6, 4.55, 7.65, 3.5)
box(ax, 6.5, .6, 'Restricted diagnostics:\nper-request authorized IDs only', width=4.1, height=.85, color=GREEN)
arrow(ax, 7.65, 2.3, 8.1, 1.45, True)
ax.text(.1, .5, 'Diamond = policy gate\nSolid = execution/data; dashed = telemetry', fontsize=16)
save(fig, 'figure-21-01-boundaries')

fig, ax = canvas(6.5)
ax.text(.1, 6.1, 'All lanes begin INSIDE an authorized universe', weight='bold')
lanes = [(4.6, 'PREFILTER', 'Task set\n{r3, r5}', 'Score that set', 'Final\n[r3, r5]'),
         (2.9, 'TASK POST3', 'Score all\nr1 ... r6', 'Shortlist\n[r1, r2, r3]', 'Task survivors\n[r3]')]
for y, title, first, second, third in lanes:
    ax.text(.1, y+.45, title, fontsize=16, weight='bold')
    for x, text in ((2, first), (5, second), (8, third)): box(ax, x, y, text, width=2.4)
    arrow(ax, 4.4, y+.5, 5, y+.5); arrow(ax, 7.4, y+.5, 8, y+.5)
ax.text(.1, 1.85, 'AUTHORIZED GRAPH TRANSIT — task acceptance differs from travel', weight='bold')
for n, text in enumerate(('u\nentry', 'x\ntransit', 'y\ntransit', 'v\ntask match')):
    box(ax, .7+2.6*n, .65, text, width=1.9, color=GREEN if n==3 else BLUE)
    if n<3: arrow(ax, 2.6+2.6*n, 1.15, 3.3+2.6*n, 1.15)
ax.text(.1, .12, 'Hand sets use Section21.6 scores; graph uses the registered four-node fixture.', fontsize=16)
save(fig, 'figure-21-02-plans')

fig, ax = plt.subplots(figsize=(11, 6))
names = ['Authorized\nsemantic', 'Exact task\nprefilter', 'Task\npost3', 'Task\npost9']
values = record['aggregates']
recall = [values[m]['macro_recall_at_2_positive'] for m in ('semantic', 'prefilter', 'post3', 'post9')]
oracle = [values[m]['macro_oracle_recall_positive'] for m in ('semantic', 'prefilter', 'post3', 'post9')]
x = list(range(4))
b1 = ax.bar([n-.19 for n in x], recall, width=.36, label='Judged relevance Recall@2 (9 positives)', color=BLUE)
b2 = ax.bar([n+.19 for n in x], oracle, width=.36, label='Eligible exact-oracle recall (9 positives)', color=ORANGE, hatch='//')
ax.bar_label(b1, fmt='%.3f', padding=4, fontsize=16)
ax.bar_label(b2, fmt='%.3f', padding=4, fontsize=16)
ax.axhline((8+2/3)/9, color=GREEN, linestyle=':', linewidth=2)
ax.set(xticks=x, xticklabels=names, ylim=(0, 1.12), ylabel='Macro recall (fraction)',
       title='ch21-metadata-predicates-v1 — same task, different plan')
fig.legend(loc='lower center', bbox_to_anchor=(.5, .12), frameon=False, fontsize=16)
fig.text(.09, .025, 'Dotted: .963 relevance ceiling at k2; three repeats.\nNo independent confidence interval or interpolation.', fontsize=16)
fig.subplots_adjust(bottom=.34, top=.87, left=.10, right=.98)
save(fig, 'figure-21-03-quality', layout=False)

fig, ax = canvas(6.6)
ax.text(.1, 6.2, 'a-day8 / post3 — first loss is the shortlist cutoff', weight='bold')
sample = next(s for s in record['samples'] if s['query_id']=='a-day8' and s['mode']=='post3' and s['trial_id']==0)
snapshot = json.loads((ROOT/'projects/V6/index_ch21/index.json').read_text('utf-8'))
source = {r['item_id']: r['source_id'] for r in snapshot['rows']}
pool = [(source[i], score) for i, score in zip(sample['raw_candidate_ids'], sample['raw_candidate_scores'])]
ax.text(.2, 5.65, '10 authorized scores', weight='bold')
for n, (name, score) in enumerate(pool[:7]):
    ax.text(.3, 5.22-n*.47, f'{n+1}. {name}   {score:.5f}', color=GREEN if name=='A08' else INK, weight='bold' if name=='A08' else 'normal')
box(ax, 3.5, 4.5, 'Shortlist top3:\nA07, A05, A06', width=2.7, height=1.05)
box(ax, 7.1, 4.5, 'Task survivors:\nempty', width=3, height=1.05)
arrow(ax, 2.85, 5, 3.5, 5); arrow(ax, 6.2, 5, 7.1, 5)
box(ax, 7.1, 2.6, 'Final / context:\nempty', width=3, height=1.05)
arrow(ax, 8.6, 4.5, 8.6, 3.65)
ax.text(3.5, 3.5, 'A08 is outside top3.\nIts task membership is known;\nits raw score was observed.', color=GREEN)
box(ax, 3.5, .55, 'Exact prefilter:\nscore and return A08', width=3.25, height=1)
ax.text(7.1, .8, 'task_count = 1\nreason: shortlist_underfill', fontsize=16)
save(fig, 'figure-21-04-loss')
