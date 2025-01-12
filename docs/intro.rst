Introduction
############

What is DeepHunter?
*******************
DeepHunter is a platform that automates the execution of threat hunting analytics via daily campaigns. It has been initially developed to automate the execution of PowerQueries using the API of the SentinelOne EDR, but it may be used with other EDR (provided you adjust the code). Threat hunting analytics include a description, tags, threat hunting notes, a query (a PowerQuery in the case of SentinelOne EDR), the threat coverage (OS, vulnerabilities, threat actors, threats), the MITRE coverage, an emulation and validation plan and references (e.g., links to online resources). Having all this information for every threat hunting analytics allows to filter/group them into hunt packages. It can be useful to check how many analytics you have for a given threat actor or a particular MITRE technique, or a combination of several criteria.

Campaigns are cron jobs running every day at the same time. They execute the analytics, and collects statistics (number of matching events, number of endpoints, etc.) for each analytic everyday for the last 24 hours, allowing to build a baseline (trend analysis) for each analytic. A model based on z-score is applied to these statistics to identify abormal values in the timeline.

DeepHunter comes with several modules that are particularly useful for threat hunters and incident responders:

- the `timeline view <usage_timeline.html>`_ shows the distribution of matches against analytics for a particular host. For each match, a box will be shown for the given date, and double clicking on it will replay the query directly in your EDR, for the selected date. Each day, campaigns will also gather the storylineID information (a special information collected by SentinelOne), which is used to highlight analytics with the same storylineID in the timeline.
- the `trend analysis <usage_trend.html>`_ module is composed of graphs showing the distribution of the number of hits, and number of endpoints, with various filters (defined by the `CUSTOM_FIELDS` property) over time. It quickly allows the threat hunter understand how frequent a threat hunting analytic triggers. A mathematical model is applied to the series to highlight potential statistical anomalies.
- the `netview (network view) <usage_netview.html>`_ module shows the list of network outbound connections for a particular host. For each IP, the popularity (number of endpoints in your environment where this destination is contacted) is shown, and for public IPs, a whois information is available, as well as the VirusTotal IP reputation.

Besides the modules, there are also some tools, which list you may enrich:

- VirusTotal Hash Checker: takes a list of file hashes and compares each against the VirusTotal database.
- LOLDriver Hash Checker: check a list of hashes agaist the LOLDriver database to confirm whether they correspond to vulnerable drivers.
- Whois: whois module developed in python.

Who is DeepHunter for?
**********************
DeepHunter is an application developed by threat hunters for threat hunters. It is not intended to be a SIEM platform, but it can help incident responders and SOC analysts during investigations.

Architecture
************
.. image:: img/deephunter_architecture.jpg
  :width: 600
  :alt: DeepHunter architecture diagram

Static vs Dynamic analytics
***************************

By default, threat hunting analytics you will create in DeepHunter will be static. They will match a hunting query that is stored in the database, and that will be executed daily by the campaigns cron job.

However, it may happen that part of hunting queries need to be dynamically generated. DeepHunter is shipped with an example (vulnerable_driver_name_detected_loldriver) of such a query. The query for this analytic is dynamically built from a script (``./qm/scripts/vulnerable_driver_name_detected_loldriver.py``) that runs prior to each campaign. This hunting query is built from an updated list of file names matching known vulnerable drivers, published on the LOLDriver website.

Dynamic queries should have the flag "Dyn. query" enabled (which is just an indication, there is no control associated to this flag), to indicate that they should not be manually edited in DeepHunter. Modifications should be done through their corresponding scripts directly.