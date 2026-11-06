# cd-lab-infrastructure

The on-prem lab host as code: a Lenovo M75q Gen 2 (32 GB RAM, 1 TB NVMe) on Ubuntu 26.04 with KVM. This root does for the lab what `cd-oci-infrastructure` does for the cloud host.

## What it defines

- **Seven isolated networks** (`lab-tier0`, `lab-tier2`, `lab-attack`, `lab-dmz`, `lab-mgmt`, `lab-detonate`, `lab-k8s`) and one NAT network (`lab-wan`). Only the OPNsense VM joins `lab-wan`; it is the sole router, firewall and DHCP server, so every hop between segments is a logged firewall decision.
- **Twelve VMs**, all left stopped: OPNsense, a Windows domain (DC01, CA01, WS01, WS02), the permanent Win 11 Pro box, Kali, Rocky, a k3s host, FLARE-VM, REMnux and CAPE's detonation guest. Disks are thin qcow2 in the `default` pool on the internal NVMe.
- **Profiles** (`ad`, `web`, `blue`, `re`, `air`) name which VMs run together. `scripts/lab up <profile>` starts them; the `profiles` output shows the RAM each needs. 32 GB runs one profile at a time.

## What it does not do

- Install anything inside a VM. Phase 1 installs by hand from the ISO and takes a golden snapshot. Phase 2 (Packer for the images, Ansible for the domain) replaces the hand install when the first eval license expires.
- Run on the Mac. The provider talks to libvirt on the Lenovo: `qemu:///system` there, `qemu+ssh://<user>@lab/system` from the Mac over the same key-only SSH the lab sync uses.
- Touch the home LAN. Sensors (Kismet with the Alfa adapter, the airspace parser) run on the host and see the house through its NIC.

## Run

```sh
cp backend.hcl.example backend.hcl   # fill in; gitignored
terraform init -backend-config=backend.hcl
terraform plan
terraform apply
../../scripts/lab up ad
```

ISO file names in `vms.tf` are what `/srv/lab/iso` on the Lenovo must hold, copied from the T7's `CYBER/iso`.

## Status

Written 2026-11-06 before the Lenovo arrived. `terraform validate` passes on provider dmacvicar/libvirt 0.8.3; a real `plan` and `apply` wait for the host. Expect the OVMF paths and the OPNsense interface order to need one correction on first apply. The provider's 0.9 line is a rewrite with a different schema (attributes that mirror libvirt's XML); migrate to it once the lab is stable, not before.
