STATUS: complete — chat Markdown deliverable

# ULW-Research Synthesis: VPS and web-hosting comparison

## Executive summary

For Korean or broadly distributed traffic and an SSH-first, panel-free workflow, Vultr is the strongest operational default because it publishes a Seoul region and mature API/CLI/Terraform surface; its exact plan price must be confirmed in the selected region/cart. Hostinger VPS is the price leader for the requested resources on the observed storefront, but it is prepaid, promotional/renewal-sensitive, and does not publish a Korea/Japan/Singapore VPS location. Paid OCI is a strong Korea-region automation option; Always Free misses the requested 16GB/4–8-vCPU target. GreenCloud is viable only after exact SKU/stock/fair-use validation and is not the clean price winner at a conventional 200GB Linux VPS target.

## Comparison table

| Provider | Closest verified fit | Current price interpretation | Region conclusion | SSH/root and automation conclusion |
|---|---|---|---|---|
| Vultr | Regular Performance 6vCPU/16GB/320GB SSD US$80/month; High Frequency 4vCPU/16GB/384GB NVMe or High Performance 8vCPU/16GB/350GB NVMe US$96/month. | Region-specific rate/availability must still be checked; normal servers bill hourly up to 672h and stopped instances bill until destroyed. | 33 live regions; Seoul included. Plan availability varies by region. | Root-capable Compute; strong REST/CLI/Terraform. |
| Hostinger VPS | KVM 4: 4vCPU, 16GB, 200GB NVMe, 16TB. | Observed US$12.99/month display; card says US$28.99/month renewal for 2 years. Prepaid; first-term total, VAT and selected term are checkout-gated. | 10 VPS locations; Asia: India/Indonesia/Malaysia. No current Korea/Japan/Singapore published. | Root/self-managed; API CLI/Terraform; native VPS terminal Agent. |
| OCI | Paid E4 Flex: 4vCPU/16GB derived about US$70.80/month before storage/network. | Usage-based; 200GB capacity fits current Free Tier entitlement, but Always Free compute is only 2vCPU/12GB. | Seoul and Chuncheon commercial regions; capacity is shape/tenancy-dependent. | sudo-capable default user, direct root SSH off by default; strongest API/CLI/Terraform surface. |
| GreenCloud | No clean conventional Linux 200GB target fit verified. MAC-4 exact hardware is US$150/month but macOS. | Live catalog/inventory and terms are volatile; many 16GB/8-core Linux alternatives only have 120–160GB. | No Seoul published; Tokyo/Singapore/HK/Vietnam options depend on SKU and stock. | KVM root access; panel-first, no documented infrastructure API/CLI/Terraform equivalent. |

## Findings by provider

### Vultr

### Hostinger

### Oracle Cloud

### GreenCloud

## Price, promotion, and renewal caveats

## Root access and managed-service boundaries

## Recommendation by operational priority

## Sources

1. https://www.hostinger.com/vps-hosting#pricing
2. https://www.hostinger.com/support/1583267-where-are-hostinger-servers-located/#vps-hosting-plans
3. https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
4. https://www.oracle.com/cloud/iaas-paas/
5. https://status.vultr.com/status.json
6. https://docs.vultr.com/reference/vultr-cli/regions/availability
7. https://greencloudvps.com/billing/store/epyc-cloud-resources
8. https://greencloudvps.com/data-centers.php
9. https://www.hostinger.com/support/8311982-what-is-managed-hosting-in-hostinger/
10. https://docs.oracle.com/en-us/iaas/Content/Compute/References/images.htm
11. https://www.vultr.com/pricing/#cloud-compute
12. https://docs.vultr.com/support/platform/billing/how-am-i-billed-for-my-servers

## Contradictions and gaps

## Expansion trace

Wave 1: 14 dedicated source lanes. Wave 2: Hostinger term, OCI storage, GreenCloud resource-model ambiguity. Wave 3: all three public-research boundaries closed with no additional leads.
