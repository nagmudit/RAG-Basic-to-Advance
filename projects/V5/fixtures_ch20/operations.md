# Deployment operations manual

## Blue rollout

The release coordinator owns Blue rollouts. Blue deployment requests use form B-17 and require an approval ticket. Operators attach the ticket identifier to the run log before starting work. The ordinary waiting period is thirty minutes after approval. A scheduled drill follows the ordinary waiting period. The monitoring team observes traffic during the wait and records each health check.

An emergency Blue rollback may start immediately when two responders confirm customer impact. This exception does not permit a routine deployment without approval. The responders record the incident identifier and the decision in the same run log. A rollback returns to the previously signed release. An unsigned experimental build is never the rollback target.

## Green rollout

The maintenance coordinator owns Green rollouts. Green deployment requests use form G-29 and require an approval ticket. The ordinary waiting period is ninety minutes after approval. Green rollouts have no emergency waiting-period exception. Operators attach the change identifier and record the planned region before work. The coordinator checks that the maintenance window remains open through completion.

When a Green rollout fails its health check, stop the rollout and notify the maintenance coordinator. Do not apply the Blue emergency exception to Green work. A stopped Green rollout requires a fresh approval before another attempt. The operations log preserves the failed check and its timestamp instead of replacing them with the successful retry.

## Billing boundary

The invoice batch freezes at 17:00 UTC. A ticket submitted at 17:00 UTC belongs to the next batch. Tickets submitted earlier belong to the current batch only when verification is complete. The literal boundary is inclusive for the next batch. Local display times are not the batch clock. A verified ticket retains the original submission timestamp and the verification timestamp as separate fields.

## Drill evidence

The drill lead records the form identifier and the signed release before starting a Blue drill. After the drill, the observer attaches a health report. The report must include the target region, observed error rate and rollback outcome. The run log and health report are complementary evidence. An empty report does not prove that no errors occurred. Record a missing observation explicitly.

## Historical discussion

Earlier planning notes discussed a ten-minute wait for all colors. That proposal was not adopted. The current Blue and Green procedures above govern operations. A search result mentioning a short wait must retain this rejection and its source section. Historical examples explain decisions but do not override the current approved procedure. These notes are part of this fictional book fixture, not a real service policy.
