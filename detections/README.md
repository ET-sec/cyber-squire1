# detections

The detection library: portable Sigma rules in three families, and the Falco
rules the sensor loads on the host. These are what the platform watches for,
kept as code beside the system they watch.

<!-- MANIFEST:detections -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `detections/falco/**` | active | Runtime rules for the host: unexpected outbound traffic from the automation container, and the measured host noise exceptions that keep it quiet. |
| `detections/sigma/**` | active | Portable detection rules in three families: edge and access events, host and container behaviour, and the AI specific rules covering injection, PII blocks, and cost ceiling breaches. |
<!-- /MANIFEST -->

`scripts/build_metrics.py` counts the Sigma rules into `metrics.yaml`, so the
number published on the site is the number of files in this tree. The AI family
under `detections/sigma/squire/` covers prompt injection, personal data blocks,
and cost ceiling breaches, which is the part of a detection library that is hard
to find anywhere else.
