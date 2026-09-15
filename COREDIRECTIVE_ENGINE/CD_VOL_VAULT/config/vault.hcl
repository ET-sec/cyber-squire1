# Vault server configuration, the single source (plan 24-02). The compose block
# no longer carries VAULT_LOCAL_CONFIG, so nothing else is loaded beside this.
#
# Seal: OCI KMS through the instance principal. The seal key id and the two KMS
# endpoints are identifiers this repository does not carry; the ocikms seal reads
# them from VAULT_OCIKMS_SEAL_KEY_ID, VAULT_OCIKMS_CRYPTO_ENDPOINT and
# VAULT_OCIKMS_MANAGEMENT_ENDPOINT, set in the host environment file the compose
# block loads. No unseal material exists on the host.
#
# Audit: the file audit device is enabled through the API after the first unseal
# (vault audit enable file file_path=/vault/logs/audit.log); audit devices are
# not a server configuration stanza.

ui            = true
disable_mlock = true   # container with no swap; keeps the block free of IPC_LOCK

listener "tcp" {
  address     = "0.0.0.0:8200"
  # Decided in DR-07: the listener is reachable only on the compose network and
  # a loopback publish, and TLS terminates at the edge. A certificate inside the
  # container would have to be distributed to every client on that network for
  # no path that leaves the host.
  tls_disable = true
}

storage "file" {
  path = "/vault/data"
}

seal "ocikms" {
  auth_type_api_key = "false"   # instance principal, never an API key on disk
}

api_addr = "http://cd-service-vault:8200"

max_lease_ttl     = "168h"
default_lease_ttl = "1h"
