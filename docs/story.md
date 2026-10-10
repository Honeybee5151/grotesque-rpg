# Story (v0)

Owner: `world`. Regions and people are in `docs/world.md`.

## The spine
The hero can't speak, and nobody knows why. Each region gossips its own theory and gives him its own
name. **The truth, revealed late:** his voice was taken, and someone is using it. In Clamour the city's
beloved Herald speaks with a voice that was never his - and the hero recognises it before anyone else
does. Who took it, and how it's paid back, is still open.

Riders - things like the Sucker Frog that climb onto people and wear them - are spreading up out of
the water. The hero meets the first one in the prologue. Whether riders and the stolen voice share a
source is a thread to pull later, not a promise yet.

**Act one: the Examination** (Miles, 2026-10-10). After the prologue the hero finds a **poster**, and
it sends him on a journey to a great Examination in the spirit of Hunter x Hunter's Hunter Exam: open
to anyone, dangerous, run in phases by eccentric examiners, crowded with rival applicants. Proposal
(not decided): the poster is folded in the drowned man's own coat - the only clue to where he was
going before the fen took his voice - and the Examination's phases are the regions, so the journey
crosses Plenty, the Hush and Clamour. A mute applicant in a crowd of talkers: examiners and rivals
read his silence as menace, wisdom or contempt. "Then we go from there."

## Prologue: Hollowell (the tutorial) - built
Goal: teach walking, gestures and the Host's telegraph, and make the Host land by letting the player
know the man first. Code: `scripts/world/maps/hollowell.gd`, `well_cave.gd`.

0. Black screen: *They pulled him out of the fen at dusk. He coughed up black water, and nothing else.*
1. Hollowell at night. Moth stares from her doorway. Odo is at the well with rope and lantern.
2. **Odo** (the gesture tutorial). He talks for both of them, asks if the hero can talk, and decides
   the answers for him. The water tastes of pennies (folk wished pennies down the well; something kept
   them - the Penny Leeches), the bucket came up full of black spawn, so he's going down. Rope
   signals: **one tug, I'm fine; two tugs, haul me up.** Silence counts as a yes - "That's the law. I
   just made it." He climbs down.
3. **The rope.** One tug. One tug. Two. The hero hauls, and the rope comes up light, its end wet, warm
   and bitten through.
4. He climbs down (a nod to himself).
5. **The well cave.** Odo's lantern still burns on a rock. The Host lurches out of the dark. Battle
   intro: *Odo staggers out of the dark. / Something wet rides his back. / He says nothing. For once.*
   Lash, coil (telegraph), latch; guard after the coil and the frog is stunned. The hero has one
   skill here, Crush.
6. **Whether Odo lives is the tutorial's real test.** Kill the frog while it is stunned (guard, then
   Crush) and the battle reports `freed`: *He's still breathing.* Kill it any other way: *He was
   already gone.* (fights tuned it: read the telegraph and Crush the stun, and he lives every time.)
   The hero takes Odo's lantern either way.
7. **If Odo died**, he climbs up alone. **Moth:** "Where's my da?" He answers with his hands, and the
   answer decides what the village thinks of the man who came up instead (`moth_read`):
   - Show the lantern - she understands (**grief**).
   - Shake his head, or say nothing - she understands, and hates that he can't say it (**grief**).
   - Point down the well, or nod - she hears that he's alive (**hope**); asked again, she calls down
     the well until her voice gives out.
   - Point at himself - she hears a confession (**blame**).
   - Shrug - he doesn't care (**cold**).
8. **If Odo lives**, the hero hauls him up the rungs. He is drained pale, with a raw pink ring on his
   crown where the sucker sat, and **he can no longer speak**: the chatterbox is as mute as the hero.
   Moth runs to him; he opens his mouth and nothing comes out. She asks the hero what happened:
   pointing at the well or at Odo, or showing the lamp, tells her (**truth**); pointing at himself, she
   hears a confession - and Odo catches her arm and shakes his head, his first gesture (**truth**);
   a shrug (**cold**); saying nothing - "Now there's two of you." (**two**). Odo nods to the hero, once.
   *Odo never says another word. He doesn't need to.* Flag `odo_freed`: he can come back later.
9. End card, then the title screen. Next: the poster.

## Open threads
- The poster and the Examination: who runs it, what passing grants, where it's held.
- What the riders want, and where they come from (the Brood under the fen is one answer).
- Who in Hollowell knows something about the hero's arrival.
- Odo alive and mute: where he turns up again.
