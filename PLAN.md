## Plan: H5Games AzGames Template

TL;DR - Turn `h5games_poki2_azgames` into a reusable HTML games-collection template enabling quick game embedding, Cloudflare/GitHub Pages deploy, and simple domain migration. Approach: parameterize configs, centralize embed logic, provide CI examples, and add clear docs + migration checklist.

**Steps**
1. Normalize project metadata: update `package.json` scripts to accept env vars (`SITE_DOMAIN`, `RESOURCE_SITE`, `PROJECT_NAME`).
2. Parameterize deployment config: make `wrangler.pages.toml` accept placeholders and document how to replace for Cloudflare/GitHub Pages/Netlify. (*depends on step 1*)
3. Remove or generalize `public/CNAME` (add `CNAME.example`) and document domain migration steps (DNS, Cloudflare verification, TLS). (*parallel with step 2*)
4. Centralize embed iframe: modify `src/templates/play.html` to use a single `{{RESOURCE_URL}}` token and add a fallback local path for offline testing. (*depends on step 1*)
5. Provide a minimal sample site: create `examples/minimal/` with a simple index + play page and a tiny `package.json` for `npm run build` to preview locally. (*parallel with step 4*)
6. Add CI workflow templates: supply `workflows/cloudflare-pages.yml` and `workflows/github-pages.yml` with documented env var usage. (*depends on steps 1-3*)
7. Update README: include quickstart (embed one game), deploy commands (Cloudflare/GH Pages), and domain migration checklist.
8. Verification: run `scripts/validate-embeds.js`, build the minimal example, and optionally run a Cloudflare Pages dry deploy (token required).

**Relevant files**
- `h5games_poki2_azgames/package.json` — change scripts & add env var usage
- `h5games_poki2_azgames/wrangler.pages.toml` — parameterize project name & build dir
- `h5games_poki2_azgames/public/CNAME` — remove or rename to `CNAME.example`
- `h5games_poki2_azgames/src/templates/play.html` — centralize iframe embed token
- `h5games_poki2_azgames/scripts/*.js` — expose `RESOURCE_SITE` and `SITE_DOMAIN` usage
- `h5games_poki2_azgames/.github/workflows/deploy.yml` — provide 2 variants (Cloudflare & GitHub Pages)
- `h5games_poki2_azgames/README.md` — document quickstart, deploy, domain migration

**Verification**
1. Run `node scripts/validate-embeds.js` and confirm no >5% invalid embeds.
2. Build minimal example: `npm run build` in `examples/minimal/` and open `dist/index.html` locally.
3. Run `wrangler pages publish dist --project-name=<test>` (requires token) to verify Cloudflare deploy steps.
4. Test domain migration steps by creating `CNAME.example` and following docs to add custom domain in Cloudflare Pages (manual verification).

**Decisions / Assumptions**
- Template consumers will have Node.js and optional Cloudflare account/token.
- Keep current embed validation scripts; do not change embed sources.
- Provide both Cloudflare Pages and GitHub Pages CI examples; Netlify optional.

**Further Considerations**
1. Do you prefer Cloudflare Pages as the primary deploy target or GitHub Pages? (Recommended: Cloudflare Pages for built-in custom domain + edge performance.)
2. Do you want automated domain verification steps scripted (requires API tokens)?
## Plan: H5Games AzGames Template

TL;DR - Turn `h5games_poki2_azgames` into a reusable HTML games-collection template enabling quick game embedding, Cloudflare/GitHub Pages deploy, and simple domain migration. Approach: parameterize configs, centralize embed logic, provide CI examples, and add clear docs + migration checklist.

**Steps**
1. Normalize project metadata: update `package.json` scripts to accept env vars (`SITE_DOMAIN`, `RESOURCE_SITE`, `PROJECT_NAME`).
2. Parameterize deployment config: make `wrangler.pages.toml` accept placeholders and document how to replace for Cloudflare/GitHub Pages/Netlify. (*depends on step 1*)
3. Remove or generalize `public/CNAME` (add `CNAME.example`) and document domain migration steps (DNS, Cloudflare verification, TLS). (*parallel with step 2*)
4. Centralize embed iframe: modify `src/templates/play.html` to use a single `{{RESOURCE_URL}}` token and add a fallback local path for offline testing. (*depends on step 1*)
5. Provide a minimal sample site: create `examples/minimal/` with a simple index + play page and a tiny `package.json` for `npm run build` to preview locally. (*parallel with step 4*)
6. Add CI workflow templates: supply `workflows/cloudflare-pages.yml` and `workflows/github-pages.yml` with documented env var usage. (*depends on steps 1-3*)
7. Update README: include quickstart (embed one game), deploy commands (Cloudflare/GH Pages), and domain migration checklist.
8. Verification: run `scripts/validate-embeds.js`, build the minimal example, and optionally run a Cloudflare Pages dry deploy (token required).

**Relevant files**
- `h5games_poki2_azgames/package.json` — change scripts & add env var usage
- `h5games_poki2_azgames/wrangler.pages.toml` — parameterize project name & build dir
- `h5games_poki2_azgames/public/CNAME` — remove or rename to `CNAME.example`
- `h5games_poki2_azgames/src/templates/play.html` — centralize iframe embed token
- `h5games_poki2_azgames/scripts/*.js` — expose `RESOURCE_SITE` and `SITE_DOMAIN` usage
- `h5games_poki2_azgames/.github/workflows/deploy.yml` — provide 2 variants (Cloudflare & GitHub Pages)
- `h5games_poki2_azgames/README.md` — document quickstart, deploy, domain migration

**Verification**
1. Run `node scripts/validate-embeds.js` and confirm no >5% invalid embeds.
2. Build minimal example: `npm run build` in `examples/minimal/` and open `dist/index.html` locally.
3. Run `wrangler pages publish dist --project-name=<test>` (requires token) to verify Cloudflare deploy steps.
4. Test domain migration steps by creating `CNAME.example` and following docs to add custom domain in Cloudflare Pages (manual verification).

**Decisions / Assumptions**
- Template consumers will have Node.js and optional Cloudflare account/token.
- Keep current embed validation scripts; do not change embed sources.
- Provide both Cloudflare Pages and GitHub Pages CI examples; Netlify optional.

**Further Considerations**
1. Do you prefer Cloudflare Pages as the primary deploy target or GitHub Pages? (Recommended: Cloudflare Pages for built-in custom domain + edge performance.)
2. Do you want automated domain verification steps scripted (requires API tokens)?
