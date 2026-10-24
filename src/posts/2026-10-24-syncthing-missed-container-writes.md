title: Syncthing didn't see the files my container wrote
summary: A download worked and the file was on the server, but it never reached my other machine until I forced a rescan.

## Goal

I built a small web page that saves a link's video or images into a folder on my home server. A Docker container does the saving, and Syncthing copies that folder to my main computer, where the next step picks the files up. The goal was simple: paste a link, and have the file arrive on my computer within a minute or so.

## Steps

1. **Test the chain end to end** with a harmless public video. The page said it had saved the file, and the file was in the folder on the server.
2. **Wait for it to arrive.** After three minutes the other machine still had nothing.
3. **Rule out the obvious.** Syncthing's status for that folder was idle, with no errors and no files waiting. The two machines were connected. The file watcher was switched on, with a 10-second delay.
4. **Ask Syncthing what it knew.** I listed the folder through its API, and the file was not in its database at all. Syncthing had never noticed it.
5. **Force a scan of just that folder** through the API. The file synced to my computer within seconds.
6. **Automate the workaround.** A one-line script asks Syncthing to rescan only that subfolder, and a cron entry runs it every minute. It reads Syncthing's API key from its own config file at run time, so the key is not stored in the script, and it prints nothing when it works.
7. **Test it again.** A new download reached my computer in about 30 seconds.

## Snag

I never found out why the watcher missed the file. The container writes through a bind mount, and my guess is that those writes do not produce the events the watcher listens for, but I did not prove that. So this is a workaround, not a root-cause fix, and it costs a rescan of one small folder every minute.

There was a second problem on the way. The first test hung. The container could not fetch the download link the service handed back, because that link used the server's own network address, and the container could not reach its own host that way. I changed the page to fetch through the internal service name instead. I suspect the host's firewall, but I did not confirm it.

## Next time

- Test the whole chain with a real file before calling a feature finished. The container log said everything was fine.
- When a sync does not happen, ask the sync tool what it knows about the file before checking anything else. "Not in its database" narrowed it down in one query.
- Say plainly in the notes when a fix is a workaround, so the question stays visible.
- If I rebuild this, have the container write somewhere Syncthing definitely watches, or trigger the rescan from the same place that saves the file.
