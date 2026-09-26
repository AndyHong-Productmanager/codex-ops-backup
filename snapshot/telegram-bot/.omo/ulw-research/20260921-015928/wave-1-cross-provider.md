# Wave 1 — cross-provider digest

- Root boundary: Vultr Compute, Hostinger VPS, OCI Compute, and GreenCloud KVM are self-managed/root-capable products. Hostinger Web/Cloud SSH is restricted, so it is not a substitute for VPS root. Sources: Vultr/Hostinger/Oracle/GreenCloud docs recorded in worker return `root_access`.
- Oracle: current Always Free A1 is 2 OCPU/12 GB, below target. Paid E4 Flex 4vCPU/16GB was derived at US$70.80/month before storage/network extras; conventional root administration is through sudo, not direct root SSH.
- Oracle regions: Seoul and Chuncheon are commercial regions, but region listing does not assure exact-shape capacity; paid reservations are the capacity assurance mechanism.
- GreenCloud: strict 16GB/8-core/200GB hardware match is MAC-4 at US$150/month, unsuitable as a normal Linux VPS choice; live 16GB/8-core cloud-resource allocation was US$40/month with 160GB and is a pool, not a single conventional VPS. Exact product and inventory must be checked in cart.
- GreenCloud regions: current table names APAC locations in Tokyo, Singapore, Hong Kong, Vietnam and Sydney, but not Seoul. Product location menus do not guarantee stock.
- Pricing cross-check: Vultr exact card was unavailable to primary verification. Independent candidates must therefore not be presented as confirmed shopping quotes; Vultr console/cart is decisive. Hostinger card offers are dynamic, prepaid and regional. GreenCloud policy makes offers and stock time-sensitive.
- Workload fit: the requested resource level is an assumed starting point for a bounded single-node Docker/Nginx/DB workload, not a throughput guarantee. Budget disk for WAL/logs/images and retain tested off-host backup.
- Red team: Oracle Always Free should be lab/secondary only; GreenCloud's shared KVM/fair-use and stock policies make it conditionally price-led; for Korean latency, direct Seoul compute favors Vultr or paid OCI subject to capacity and cart verification.

Key source URLs are retained in the worker transcripts and named Wave 1 artifact files.
