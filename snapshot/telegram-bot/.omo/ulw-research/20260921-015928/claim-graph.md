# Claim graph

## Verified claims

_No claims are verified before research waves complete._

## Nodes

| claim_id | statement | type | risk | intent | supporting observations | independence | counter-search | primary source | status |
|---|---|---|---|---|---|---|---|---|---|
| C-01 | Vultr has a Seoul region, but the requested plan must be checked for regional availability at provisioning time. | factual | normal | I-01 | O-01 | official status + CLI docs; primary-only exception | plan availability is explicitly queried per region/plan | Vultr CLI availability docs | supported |
| C-02 | Hostinger KVM 4 matches target resources on the observed storefront, but its promotion is not universal or a confirmed initial-term total. | pricing | high | I-01,I-03 | O-02 | product card + limits support page | regional storefronts differ; initial term unclear | Hostinger pricing card | partial |
| C-03 | Hostinger currently does not publish a Korea/Japan/Singapore VPS location. | factual | normal | I-01 | O-03 | current matrix + historical counter-search | stale historical pages rejected | Hostinger support matrix | supported |
| C-04 | OCI Always Free does not meet 4–8 vCPU/16 GB; paid OCI Flex pricing needs a region-specific quote. | pricing | high | I-01 | O-04 | price table + free-tier documentation | old 4 OCPU/24 GB claim rejected | Oracle price/free-tier docs | partial |
| C-05 | All four providers have self-managed products that fit SSH-first administration, but Hostinger Web/Cloud lacks root and must be excluded from the VPS comparison. | factual | normal | I-02 | O-05 | official product classification + SSH scope | VPS is the counterexample within Hostinger | Hostinger managed-hosting docs | supported |
| C-06 | GreenCloud's US$40 16GB/8-core offering is a resource pool with 160GB, not a proven direct 200GB VPS equivalent. | factual | normal | I-01 | O-06 | live catalog primary-only exception | no fixed single-VPS proof | GreenCloud live catalog | supported |
| C-07 | OCI Seoul is a viable region listing but not a capacity guarantee for target shape. | factual | normal | I-01 | O-07 | official region + capacity policy | official capacity docs disconfirm inference | Oracle region/capacity docs | supported |
| C-08 | Hostinger's KVM 4 US$12.99 display cannot be converted into a verified initial total or duration from public pages. | pricing | high | I-03 | O-02 + wave-2-expansions.md | public product + terms | direct counter-search exhausted; checkout is decisive | Hostinger KVM 4 card | supported non-proof |
| C-09 | Current OCI free capacity entitlement is 200GB combined boot/block, while free VPU performance billing is unresolved. | pricing | high | I-01 | wave-2-expansions.md | current docs + live API; PDF conflict recorded | live API/product docs support 200GB; VPU no explicit answer | Oracle Always Free docs | partial |
| C-10 | GreenCloud Cloud Resource 2 must not be compared as a direct one-VM 16GB/8-core/160GB VPS. | factual | normal | I-01 | O-06 + wave-2-expansions.md | product page + catalog | no evidence supports full allocation to one VM | GreenCloud product page | supported |
| C-11 | Vultr has current conventional plans that meet the requested target from US$80/month before options/tax, with a Seoul region. | pricing | high | I-01 | O-01,O-08 | live region status + browser-rendered live pricing | pricing and availability are regional | Vultr pricing table | supported |
