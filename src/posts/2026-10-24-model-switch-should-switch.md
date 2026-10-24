title: Making a model switch actually switch
summary: Two local AI backends share one GPU. Picking a model in my chat tool now starts and stops them, and cleans up when I close the window.

## Goal

I use a small terminal chat tool for local language models. One backend, Ollama, loads models on demand and unloads them after five idle minutes. The other, Strata, runs a much larger model, and it has to be started and stopped by hand. They share one graphics card and one pool of RAM, so only one can be loaded at a time.

The chat tool had a `/model` command, but all it did was point the next message at a different server. If I picked the big model I had to start it myself, and if I forgot to stop it, it sat there. Idle, it held 11.5 GB of graphics memory, about 21 GB of RAM, filled the swap, and used about 28% of a CPU core. Strata has no idle shutdown of its own. I wanted `/model` to mean what it says.

## Steps

1. **Find the exact start command.** Strata can print what it would do without doing it (`strata launch --plan`), and a "same as" line near the end of that output spells out the full command. I checked it matched the profile I had been starting by hand.
2. **Write one function that decides which backend should hold the card.** Picking the big model unloads whatever Ollama has loaded (a request with `keep_alive` set to 0), starts Strata detached from the terminal, then polls its model list every two seconds until it answers. Picking an Ollama model while Strata is up stops Strata first, waits for its port to close, then gives the card a few seconds to free its memory.
3. **Call it in two places.** On `/model`, so the switch is visible, and before every message, so one-shot questions and saved prompts behave the same way.
4. **Clean up on exit.** When the tool quits it stops Strata only if it was the one that started it, and unloads the Ollama models it used. It does nothing if another copy of the tool is still running. Two environment variables turn the switching and the cleanup off.
5. **Test the decisions without touching anything real.** Two sets of cases, one for choosing a backend and one for cleaning up, with the start and stop replaced by stubs: backend up or down, each model type, both switches set, another copy running.
6. **Test it live.** From a chat on the small model, `/model strata` unloaded it and had the big model answering in 30 seconds. Going back stopped Strata first. Quitting with Ctrl-D left the machine idle.

## Snag

Closing the terminal window did not clean up. The tool was gone, but Strata was still running and still holding the card.

My theory, which I have not proved, is that closing a terminal window sends a hang-up signal to everything running in it. That includes the short helper that asks Strata to stop, so the helper was killed before it finished. The fixes were to start that helper in its own session, so the hang-up cannot reach it, to ignore repeat hang-ups while cleaning up, and to write every cleanup to a log file.

The log is what confirmed it. The second test showed the signal arriving, the cleanup starting, and Strata stopped two seconds later. Afterwards 24 GB of RAM was free, against about 2 GB while it was running.

## Next time

- Add the log before the first live test, not after the first failure.
- A cleanup step started from a terminal program dies with the terminal unless it is detached into its own session.
- Test every way of leaving, not just the polite one. Ctrl-D worked on the first try, and closing the window did not.
- Measure what a background service costs when it is idle. The memory and CPU numbers are what made this worth fixing.
