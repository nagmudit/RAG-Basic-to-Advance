"""Editable mechanism diagrams and the checked matched-workload result plot."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
plt.rcParams.update({'font.size': 16, 'svg.fonttype': 'none', 'font.family': 'DejaVu Sans'})
BLUE, ORANGE, GREEN, INK = '#245a81', '#a95418', '#27715b', '#172c3c'


def save(fig, name):
    fig.savefig(HERE/(name+'.svg'), bbox_inches='tight')
    fig.savefig(HERE/(name+'.png'), dpi=160, bbox_inches='tight')
    p = HERE/(name+'.svg')
    p.write_bytes(('\n'.join(s.rstrip() for s in p.read_text('utf-8').splitlines())+'\n').encode())
    plt.close(fig)


def canvas(height):
    fig, ax = plt.subplots(figsize=(11, height))
    ax.set(xlim=(0, 11), ylim=(0, height)); ax.axis('off')
    return fig, ax


def box(ax, x, y, text, width=3, color=BLUE, height=.9):
    ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle='round,pad=.025,rounding_size=.05',
        facecolor='#f4f7fa', edgecolor=color, linewidth=1.8))
    ax.text(x+width/2, y+height/2, text, ha='center', va='center', color=INK)


def arrow(ax, start, end, color=INK, dashed=False):
    ax.annotate('', xy=end, xytext=start, arrowprops={'arrowstyle': '->', 'linewidth': 1.7,
        'color': color, 'linestyle': '--' if dashed else '-'})


fig, axes = plt.subplots(1, 2, figsize=(11, 4.7), gridspec_kw={'width_ratios': [1.2, 1]})
ax, note = axes
ax.set(xlim=(-.12, 1.35), ylim=(-.12, 1.18), xlabel='Coordinate 1', ylabel='Coordinate 2')
ax.axhline(0, color='#c7d1db'); ax.axvline(0, color='#c7d1db')
for end, color, style in (((1, 0), BLUE, '-'), ((0, 1), ORANGE, '-'), ((1, .5), INK, '--'), ((1/1.25**.5, .5/1.25**.5), GREEN, '-')):
    ax.annotate('', xy=end, xytext=(0, 0), arrowprops={'arrowstyle': '->', 'linewidth': 2.4, 'color': color, 'linestyle': style})
ax.text(.65, -.09, 'q = (1, 0)', color=BLUE)
ax.text(.05, 1.02, 'p = (0, 1)', color=ORANGE)
ax.text(1.02, .54, 'v', color=INK)
ax.text(.62, .32, "q\N{PRIME}", color=GREEN)
ax.set_aspect('equal'); ax.set_xticks([0, .5, 1]); ax.set_yticks([0, .5, 1])
note.axis('off')
note.text(0, .9, 'ASSUMPTION → DIRECTION', weight='bold', color=INK)
note.text(0, .73, 'v = q + 0.5 p = (1, 0.5)')
note.text(0, .57, 'Norm = √1.25 ≈ 1.1180')
note.text(0, .41, "q′ ≈ (0.8944, 0.4472)", color=GREEN)
note.text(0, .16, 'Normalization preserves direction.\nWrong feedback still causes drift.', color=ORANGE)
fig.tight_layout(w_pad=1.5)
save(fig, 'figure-24-01-feedback')

fig, ax = canvas(7.5)
ax.text(.2, 7.15, 'QUERY TIME — frozen drafts in this experiment', weight='bold')
box(ax, .2, 5.9, 'Original request', width=2.6)
box(ax, 4.0, 5.8, 'Intent anchor\nfields + authority + model', width=6.6, height=1.1)
arrow(ax, (2.8, 6.35), (4, 6.35))
for x, text in ((.2, 'Original surface'), (4.0, 'Paraphrases'), (7.8, 'Hypothetical\npassage')):
    box(ax, x, 4.15, text, width=2.8)
    arrow(ax, (x+1.4, 5.65), (x+1.4, 5.06), dashed=True)
ax.plot([1.6, 9.2], [5.65, 5.65], color=INK, linewidth=1.3)
arrow(ax, (7.2, 5.8), (7.2, 5.65))
box(ax, .2, 2.5, 'Admission + budgets\noriginal fields retained', width=4.3)
box(ax, 6.0, 2.5, 'Authorized source scoring\nbranch top two', width=4.6)
for x in (1.6, 5.4, 9.2):
    arrow(ax, (x, 4.15), (2.35, 3.4))
arrow(ax, (4.5, 2.95), (6, 2.95))
box(ax, 6.0, .95, 'Interleave → cap → pack\nreal source units only', width=4.6, color=GREEN)
arrow(ax, (8.3, 2.5), (8.3, 1.85))
ax.text(.2, 1.4, 'Hypothetical text\nis never evidence.', color=ORANGE)
ax.text(.2, .2, 'INDEX TIME: approved source body → compatible corpus vector', color=BLUE)
save(fig, 'figure-24-02-anchor')

fig, ax = canvas(5.9)
ax.text(.2, 5.55, 'ABSTRACT CONTROL TASKS — no retrieval or answer generation', weight='bold')
box(ax, .35, 3.9, 'retry\nindependent', width=2.5)
box(ax, .35, 2.15, 'trust\nindependent', width=2.5)
box(ax, 4.35, 3.0, 'combine\ndepends on both', width=2.9)
arrow(ax, (2.85, 4.35), (4.35, 3.65)); arrow(ax, (2.85, 2.6), (4.35, 3.25))
ax.text(7.8, 4.5, 'Shared budget:\n2 steps', weight='bold')
ax.text(7.8, 3.65, 'After two successes:\nretry, trust complete', color=GREEN)
ax.text(7.8, 2.65, 'combine ready\nbut unexecuted', color=ORANGE)
ax.text(.35, .95, 'If retry fails: combine is blocked, while trust may still finish.', color=ORANGE)
ax.text(.35, .25, 'Validate all dependencies and cycles before scheduling any task.')
save(fig, 'figure-24-04-dependencies')

record = json.loads((ROOT/'projects/V7/chapter-24-experiment.json').read_text('utf-8'))
snapshot = json.loads((ROOT/'projects/V7/index_ch24/snapshot.json').read_text('utf-8'))
observation = next(o for o in record['per_query_trials'] if o['query_id'] == 'q07' and o['mode'] == 'multi')
parent = next(s for s in record['samples'] if s['request_id'] == observation['request_id'])
fig, ax = canvas(6.5)
ax.text(.2, 6.15, 'q07 / MULTI — ch24-frozen-reformulations-v1', weight='bold')
for j, branch in enumerate(parent['branch_shortlists']):
    x = .2+j*3.8; name = branch['branch_id']; wp = snapshot['inputs']['q07'][name]['wordpieces_with_specials']
    child = next(s for s in record['samples'] if s.get('parent_request_id') == parent['request_id'] and s.get('branch_id') == name)
    pairs = ', '.join(i.split(':')[0] for i in branch['ids'])
    box(ax, x, 4.4, f'{name}\n{wp} input WP\n{len(child["raw_candidate_ids"])} vector scores\n{pairs}', width=2.8, height=1.55)
    arrow(ax, (x+1.4, 4.4), (5.5, 3.75))
box(ax, 2.0, 2.75, 'Deduplicated admission: A17, A14, A12\nOrigins: original, rewrite-2, original', width=7.0, height=1.0)
box(ax, 3.4, 1.1, 'Cap two: A17, A14\nBoth packed (75 WP)', width=4.2, color=GREEN)
arrow(ax, (5.5, 2.75), (5.5, 2.0))
ax.text(.2, .25, '27 input WP; three searches. A12 is visible before the global cap.', color=INK)
save(fig, 'figure-24-03-fanout')

methods = ['original', 'multi', 'hypothetical']; labels = ['Original', 'Multi-query', 'Hypothetical']
fig, (quality, work) = plt.subplots(1, 2, figsize=(11, 5.5), gridspec_kw={'width_ratios': [1.3, 1]})
for j, (key, name, color) in enumerate((('union_recall', 'Union', BLUE), ('positive_recall_at_2', 'Capped', ORANGE), ('context_evidence_recall', 'Context', GREEN))):
    xs = [i+(j-1)*.22 for i in range(3)]
    values = [record['aggregates'][m][key] for m in methods]
    quality.bar(xs, values, .20, label=name, color=color)
quality.set(ylim=(0, 1.23), ylabel='Macro required-evidence recall', xticks=range(3), xticklabels=labels)
quality.legend(loc='upper center', ncol=3, fontsize=16, columnspacing=.7, handlelength=.8)
for i, m in enumerate(methods): quality.text(i, record['aggregates'][m]['union_recall']+.035, f"{record['aggregates'][m]['union_recall']:.4f}", ha='center')
quality.tick_params(axis='x', rotation=15)
counts = [record['aggregates'][m]['scored_pairs'] for m in methods]
work.bar(range(3), counts, color=[BLUE, ORANGE, GREEN], width=.58)
work.set(ylim=(0, 23), ylabel='Mean scored pairs / original task', xticks=range(3), xticklabels=labels)
work.tick_params(axis='x', rotation=15)
for i, value in enumerate(counts): work.text(i, value+.5, f'{value:.2f}', ha='center')
fig.suptitle('ch24-frozen-reformulations-v1', fontsize=16, weight='bold')
fig.tight_layout(rect=(0, .08, 1, .93), w_pad=1.6)
fig.text(.05, .015, 'Recall: 11 positive questions. Work: all 16 tasks. Three warm repeats.', fontsize=16)
save(fig, 'figure-24-05-results')
