title: Why my containers couldn't see who was connecting
summary: Every client looked like the Docker gateway. The cause was a firewall rule I did not know Tailscale had added.
date: 2026-10-24

## Goal

I run a small server at home with a set of Docker containers, reachable over a Tailscale network. A script on it records the last time a real person used each service, so I can see which ones I have stopped using. From about 10 October it reported zero live clients for everything, and the "last used" dates stopped moving. I wanted to find out why, and fix it properly rather than switch the check off.

## Steps

1. **Reproduce it.** I held a connection open to a service from another machine and read the container's own connection table (`/proc/net/tcp`). Over the LAN address the container saw my machine's real address. Over the Tailscale address it saw the Docker bridge gateway instead. My script ignores bridge addresses on purpose, because that is how it tells real clients from the monitoring tools that poll every service. So every Tailscale client was being thrown away.
2. **Look on the host.** `ss` on the host showed no connection at all. Docker's NAT delivers packets straight into the container, so the host never owns a socket. That ruled out reading host sockets as a fix.
3. **Read the firewall.** I ran a read-only script with `sudo` that printed the NAT and filter rules. Two of Tailscale's own rules explained everything:

        -A ts-forward -i tailscale0 -j MARK --set-xmark 0x40000/0xff0000
        -A ts-postrouting -m mark --mark 0x40000/0xff0000 -j MASQUERADE

    Anything arriving from the tailnet gets marked, and anything marked gets its source address rewritten to the host's own. Docker's port forwarding turns a tailnet connection into forwarded traffic, so it hit that masquerade. The nftables counter on that rule had already counted 25 packets, so it was firing.

4. **Check I did not need it.** As I read it, that rule is there for routing other machines' traffic through this one (a subnet router or exit node). My server advertises no routes and is not an exit node, so nothing should have depended on it.
5. **Change one setting, with a safety net.** Tailscale has a netfilter mode called `nodivert`: it keeps its rules but stops sending traffic through them. I wrapped `tailscale set --netfilter-mode=nodivert` in a script that reverts itself after 180 seconds unless I confirm it still works. Rollback is `tailscale set --netfilter-mode=on`.
6. **Verify.** Every published port still answered over the tailnet, a held connection now showed the real client address inside the container, and the script reported a live client again.

## Snag

My first theory was wrong. I assumed Docker's userland proxy was rewriting the source address, so I patched the script to also read the host's sockets. It found nothing, and the reason was the point: NAT leaves no socket on the host, so the patch could never have worked. I only learned that by testing with a held connection rather than trusting the theory. I never installed that patch.

The change also costs something. With `nodivert`, Tailscale's rule that drops spoofed tailnet addresses arriving from outside the tailnet no longer applies, and neither does its blanket forward accept. I tested that every container is still reachable. On a home server behind a router that trade is small, but it is a trade.

I also never proved that a Tailscale update on 10 October caused this. The dates stopped around then, so I suspect it, but I could not show it.

## Next time

- Look at the packet's source address from inside the container before assuming where it changed.
- Treat "never used" and "stale" findings from a sampler as suspect when every service flips to zero on the same day. That pattern was the clue, and a real change in how people use things would not look like that.
- Make any network change reversible by default, with an automatic timeout, before running it on a machine I am connected to through that same network.
- Real client addresses now show up in each service's own logs. That is a side benefit I did not plan for.
