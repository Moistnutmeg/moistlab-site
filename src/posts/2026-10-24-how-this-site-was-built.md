title: How this site was built
summary: A static site, a small Python builder, GitHub Pages and a free domain. What went smoothly and the three things that did not.

## Goal

I wanted a place to publish write-ups that would last, cost nothing to run, and not depend on a service I would have to maintain. That meant no framework and no database, no third-party requests when someone loads a page, and notes I could write as plain Markdown.

## Steps

1. **Pick the shape.** Markdown notes in one folder, a short Python script that turns them into plain HTML, and GitHub Pages serving the output. The builder is about 160 lines and uses one library, `markdown`.
2. **Design it in my own theme.** One font family, a self-hosted subset of the one I use in my terminal, about 33 KB per weight. The banner's background grey is also the page's background grey, so the banner melts into the page, with its edges feathered by a mask. Links invert when you hover them, like selected text in a terminal. Each page types its own command at a prompt, and that is the only animation. It takes 0.7 seconds and stops for anyone who has asked their system for reduced motion.
3. **Get a domain.** A free first-year `.dev` domain. `.dev` only works over HTTPS, which suits GitHub Pages, because it issues the certificate for you.
4. **Point the domain at GitHub.** Four A records at the registrar and one CNAME for `www`:

    | Type | Host | Value |
    |---|---|---|
    | A | (blank) | 185.199.108.153 |
    | A | (blank) | 185.199.109.153 |
    | A | (blank) | 185.199.110.153 |
    | A | (blank) | 185.199.111.153 |
    | CNAME | www | the account's `github.io` address |

5. **Turn on Pages.** In the repository settings: deploy from the `main` branch, the `/docs` folder, with the custom domain set. Then wait for the DNS check to pass and tick the HTTPS box.
6. **Check it from outside.** Every asset, the feed and the sitemap returned 200, the certificate verified, and plain `http://` redirected to `https://`.

## Snag

Three things cost me time.

- **The access token could push but not create.** My fine-grained token for the repository could write files, but creating a repository and switching on Pages through the API both returned 403. Those two steps happened in the browser instead.
- **GitHub edits your repository too.** Setting the custom domain makes GitHub commit a `CNAME` file to the branch. My next push was rejected because the remote had commits I did not. I fetched, rebased on top, and made my builder write that file exactly the way GitHub does, so the two stop disagreeing.
- **The HTTPS box lagged the certificate.** The settings page kept saying no certificate had been issued, while the site was already serving a valid one. I checked from outside with a plain request and waited for the box to unlock.

One smaller trap: my Markdown library cannot put a fenced code block inside a numbered list. The list silently falls apart from that point on. Indenting the code by eight spaces fixes it, and I only noticed because I looked at the rendered page rather than the source.

## Next time

- Look at the rendered page before pushing, not just the build output.
- Fetch before every push, because Pages can change the branch behind my back.
- Do the browser-only steps first (create the repository, switch on Pages), so the rest can be scripted.
- Check certificates and redirects from outside with plain requests, and do not trust a settings page to say they are done.
