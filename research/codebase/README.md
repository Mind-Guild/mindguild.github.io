# Mind Guild Codebase Atlas

Public route: https://mind-guild.com/research/codebase/

The page uses local HTML/CSS/JavaScript and a generated metadata snapshot. It does
not request private GitHub data from visitors or include source bodies, machine
settings, meeting contents, or credentials. Repository links are pinned to the
inspected commit and require the visitor's GitHub permissions.

## Refresh the snapshot

From this website repository, with a clean implementation checkout at the desired
commit:

```sh
python tools/build-codebase-map.py /path/to/Mind_Guild \
  --output research/codebase/map-data.js
```

The builder exports tracked-file metadata, Python top-level symbol locations, and
AST-resolved internal import pairs. Imports inside functions, optional branches,
and type checks are included. Three source-reviewed explicit loaders into the
extensionless `experiments/SR_Experiment` file are also mapped. General dynamic
imports, runtime call graphs, test outcomes, and scientific validity are not inferred.

For a verified exported source tree, pass `--manifest manifest.json` with
`repository`, `commit`, `committed`, and the GitHub recursive `tree` entries. All
Python blobs must match their Git SHA-1 before metadata is written. The inspected
source for the initial release is `a3bd51434f11e3a81b27ed68e3f922d6e9328c8e`.

Review the group descriptions in `tools/build-codebase-map.py`, the flow annotations
in `atlas.js`, and the acceptance-status paragraph in `index.html` whenever the
architecture or qualification status changes. The architecture tab shows grouped
imports; the Layer 1 tab deliberately shows data flow. The two arrow meanings are
labeled separately on the page.

The atlas is linked from `implementation.html` and `products.html`. It uses the
existing Mind Guild brand assets and publishes through the site's GitHub Pages
deployment. No Sites identity or hosting migration is required.
