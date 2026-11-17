title: A pixel-art model of my house that follows Home Assistant
summary: A Three.js cutaway of the whole house that lights its lamps from real device state, plus the 64-colour palette rule that broke my colours three different ways.

## Goal

I wanted a showpiece wall display for Home Assistant. The idea came from a post where someone hired an illustrator to draw their house, a day and a night version of every floor, with each device as its own image layer. I liked the result, but drawn layers are fixed images.

So I built mine as a live 3D scene instead: a pixel-art cutaway of the whole house, seen from one fixed corner, that reads real lamp and device states and has small things moving about in it.

![The whole house in daylight: the first floor with the office, a bedroom and the main bedroom above the open-plan kitchen and living room, and the back garden to the left.](../../assets/img/home-diorama-full.png)

*The Full view, daytime. Two floors and the garden, one fixed camera.*

![The ground floor on its own: kitchen island, stairwell, a closet with a glowing monitor, the living room and the front patio.](../../assets/img/home-diorama-ground.png)

*The Ground Floor view, which hides the floor above.*

## Steps

1. **Start from a kit.** The renderer is Three.js, using an open-source "diorama" playbook (MIT licence) that supplies a pixel-art post-processing pass and a palette system. I built the office first, on 2 November, and the rest of the house on 15 and 16 November.
2. **Build from measurements and photos.** I measured the office with a tape, and for the rest of the house I filmed one walkthrough, gave the room sizes, and sent a photo of each thing I wanted in the scene. About 40 photos went in. Props are small enough that a detail under about a pixel and a half turns to speckle, so I cut a lot of clutter.
3. **Lock the camera.** One corner, one angle, with the near walls cut away. Every layout decision follows from that: furniture gets moved, shrunk or deleted so it is not hidden behind something else, and the house is not to scale (the office is half a metre deeper than the real one, for example).
4. **Make time a lighting change.** Day and night come from Home Assistant's `sun.sun` elevation: below -6 degrees is night, above +6 is day. Nothing is swapped, the lights and window panes just dim.
5. **Animate with pure functions.** Every moving thing is a function of the clock, and only runs while its floor is on screen. The bedroom doors swing only for a cat walking through, and at night one cat at a time leaves its bedroom, walks down the stairwell to the feeder and goes back.
6. **Wire it to the house.** A small Python bridge on a home server reads a whitelist of Home Assistant entities and serves them to the page as JSON. The Home Assistant token stays on the server and the page never sees it. Lamps in the scene come on and off with the real ones, and clicking a lamp switches the real light, through a second endpoint that only accepts a short list of lamps.
7. **Test frozen frames.** The page exposes a `freeze(t)` function that draws one frame for a given time. Every check, and every picture in this post, is a frozen frame rather than a screenshot taken at a moment I could not repeat.

The clip below is the Full view at night on a black background, with the night routines running. It is rendered frame by frame from `freeze(t)`, in real time.

<video controls loop muted playsinline preload="metadata" poster="../../assets/img/home-diorama-night-poster.jpg" width="1000" height="640">
<source src="../../assets/img/home-diorama-night.webm" type="video/webm">
<source src="../../assets/img/home-diorama-night.mp4" type="video/mp4">
</video>

*A minute of the night routine, in real time.*

## Snag

The thing that cost me the most time was the palette. The pixel look comes from snapping every rendered pixel to a fixed list of 64 named colours, and a lit 3D scene does not hand that snap the colours you chose.

- **Lit colours change.** A pink or red on a wall that faced the light came out tan or grey. Anything flat, like wall art, lamps and decals, has to be drawn unlit so its palette colour shows as it is.
- **Faint things are not faint.** The snap turns any translucent glow over about 2% opacity into a hard brown blob, so the snake tank's night glow is set to 2%. A glass pane in front of a small object tinted it grey, so glass stays at 10% or less. There is no lilac and no olive in the palette at all.
- **Dusk broke two colours.** At the day and night switch, a pink chair and a red jersey went tan and brown. A small palette swap for the dusk ramp fixed it, and it moved 279 of 1,024,000 pixels in the day frames.

Two smaller ones:

- **Hiding things behind a wall.** From this camera, a sight line over a wall top drops about 0.735 m for every metre behind the wall, so anything taller than that shows over the wall. The stairwell is clipped with a plane through the wall's inner top edge, and an outward-swinging door past about 35 degrees pokes over the top, so doors swing inward.
- **A comment ate my code.** A `//` comment added to the end of a line that also held code swallowed the code. It cost me two lamp assignments once and a squid's height another time. Listing the lamp object after every edit is how I caught it.

## Next time

- Draw a crop of the render before calling a placement done. From this camera a tank or a pot hides what is behind it, and a mirror vanished behind a tank.
- Keep a rollback copy of the built page on the server before every deploy. I shipped about 60 changes in one day and the copies made each one a non-event.
- Check the browser console after touching the main file. One error was hidden by the animation loop that kept redrawing over it.
- Put the "wire it to the house" step last. Everything outside the office was static until the end, which let me argue about layout without touching Home Assistant.
