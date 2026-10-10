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

## Act one: the Salt Examination
Miles (2026-10-10): after the prologue a **poster** sends the hero to a hunter exam, as romantic as
Hunter x Hunter's - a journey just to reach it, with challenges and puzzles on the road; other
contestants once he's there; trials until he receives his certification.

**The Salt Guild** hunts riders. Where riders crawl up out of the water and wear people, Salt
Hunters go where nobody else will - drowned roads, sewn-mouthed abbeys, cities of noise - to hunt
riders, cut the ridden free, find lost things and map what isn't mapped. Children play at it. Their
licence is **the Salt**: a card of pressed salt-glass that never dissolves and opens every door. The
Examination is held once a year, never in the same place, and finding it is the first test.

**The poster** is folded in the drowned man's own coat, soaked, the ink run. It is a riddle - *held at
the end of the spring rains, where the hungry are fed and never full* (Plenty) - and its applicant
line carries a name the fen has washed away. His? Nobody can say, least of all him.

**The road there** (challenges and puzzles; each a place to meet people and test the gestures):
- The drowned road north out of Hollowell, through fog: the Mouther, Penny Leeches in the shallows.
- **The ferrywoman's question**, to cross the black water: an impossible choice ("your mother and
  your child are drowning..."). Every answer sends you back. The only way across is to say nothing -
  the mute hero has to *choose* silence, as an answer, from the menu.
- Plenty's hidden door: the Examination is entered through a butcher's that sells the Ever-Sow's
  meat. You order "the cut that grows back" - without words.

**The Examination** (hundreds of applicants with numbered salt-tags; he can't give a name, so the
registrar writes one for him). Contestants, each a different relation to mouths and silence:
- **Pim**, a kitchen boy from Plenty who talks enough for two and appoints himself the hero's voice
  (and translates his gestures wrong, cheerfully). The friend.
- **Nine**, a runaway novice from the Hush under a vow of silence who signs in the abbey's hand-speech -
  the only one who reads the hero right. Cold, exact, dangerous.
- **Old Gristle**, a thirty-time applicant whose belly-mouth laughs while his face smiles; he befriends
  rookies to ruin them.
- **The Lady and her Rider**, who lets a rider ride her by choice. They take turns speaking. The
  Examination's terror.
Phases (a proposal, each its own examiner and test): the Long Swallow (an endless tunnel under Plenty -
keep up or drop), the Tasting (hunt and cook for a glutton examiner), the Hush crossing (through the
wood where silence is consent), the Tower of Tongues in Clamour (doors that open to words: make others
speak for you), the Hunt (take another applicant's tag), and **the Concession**: duels won when your
opponent *says* "I yield" - which the hero can never say.

**Certification** in Clamour. The Salt is presented by the city's Herald - who speaks with the hero's
stolen voice. The end of act one, the start of everything else.

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
