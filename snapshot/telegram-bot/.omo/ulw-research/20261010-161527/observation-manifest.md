# Observation manifest

| observation_id | source | layer | observer group | observed_at | artifact | anchor | notes |
|---|---|---|---|---|---|---|---|
| O1 | https://sanbo.co.kr/ | HTTP | leader live probe | 2026-10-10T07:19Z | http-audit.txt | all host variants 200 | no redirect consolidation |
| O2 | https://sanbo.co.kr/sitemap.xml | HTML/crawl | crawl-index | 2026-10-10T07:18Z | agent report | 35/35 listed pages share homepage canonical | direct page-source observation |
| O3 | public search retrieval | SERP | search-serp | 2026-10-10T07:17Z | agent report | homepage retrieved for quoted target query | not a native rank measurement |
| O4 | https://booking.naver.com/booking/13/bizes/1666652 | entity | search-serp | 2026-10-10T07:18Z | agent report | matching phone/address; website points Instagram | Place backend inaccessible |
