Introduction
############

What is DeepHunter?
*******************
DeepHunter is a Threat Hunting platform that features:

- Repository for your threat hunting analytics shown in a sortable table.
- Search and filters (description, threat hunting notes, tags, query, OS coverage, vulnerabilities, threat actors, threat names, MITRE coverage, etc.) to find particular threat hunting analytics or group them into hunting packages.
- Automated execution of threat hunting queries in daily campaigns and collection of daily statistics (number of matching events, number of matching endpoints, etc).
- Trend analysis with automatic detection of statistical anomalies.
- Timeline view of the distribution of threat hunting analytics for a given endpoint.
- Network view module to analyze network activities from a host, with highlights on the destination popularity (based on your environment) and VirusTotal reputation.
- Reports (Campaigns performance report, Top endpoints identified in the last campaign, MITRE coverage, List of analytics with missing MITRE coverage)
- Tools (LOL Driver Hash Checker, VirusTotal Hash Checker, Whois).

Campaigns
*********
The purpose of DeepHunter is to automate the execution of each threat hunting analytic (the ones with the `run_daily` flag set) each day. This is done through campaigns.

Campaigns are cron jobs running every day at the same time. They execute the analytics, and collect statistics (number of matching events, number of endpoints, etc.) for each analytic every day for the last 24 hours, creating a baseline (trend analysis) for each analytic. A model based on z-score is then applied to these statistics to identify statistical anomalies in the timeline.

Statistics regeneration
***********************
It may happen that you modify a threat hunting query for various reasons (e.g., add a filter to exclude some results). When you do so, statistics for the updated query will change. If you want to apply the same logic to all past statistics, as if the query would have always been as you just changed it, you can regenerate the statistics for this threat hunting query. It will work on the background and show the percentage of completion as shown below.

.. image:: img/analytics_regen_stats.png
  :width: 1500
  :alt: DeepHunter architecture diagram

DeepHunter modules
******************
DeepHunter comes with several modules that are particularly useful for threat hunters and incident responders:

- the `timeline view <usage_timeline.html>`_ shows the distribution of matches against analytics for a particular host. For each match, a box will be shown for the given date, and double clicking on it will replay the query directly in your EDR, for the selected date. Each day, campaigns will also gather the storylineID information (a special information collected by SentinelOne), which is used to highlight analytics with the same storylineID in the timeline.
- the `trend analysis <usage_trend.html>`_ module is composed of graphs showing the distribution of the number of hits, and number of endpoints, with various filters (defined by the `CUSTOM_FIELDS` property) over time. It quickly allows the threat hunter understand how frequent a threat hunting analytic triggers. A mathematical model is applied to the series to highlight potential statistical anomalies.
- the `netview (network view) <usage_netview.html>`_ module shows the list of network outbound connections for a particular host. For each IP, the popularity (number of endpoints in your environment where this destination is contacted) is shown, and for public IPs, a whois information is available, as well as the VirusTotal IP reputation.

DeepHunter tools
****************
Besides the modules, there are also some tools, which list you may enrich:

- VirusTotal Hash Checker: takes a list of file hashes and compares each against the VirusTotal database.
- LOLDriver Hash Checker: check a list of hashes agaist the LOLDriver database to confirm whether they correspond to vulnerable drivers.
- Whois: whois module developed in python.

Who is DeepHunter for?
**********************
DeepHunter is an application developed by threat hunters for threat hunters. It is not intended to be a SIEM platform, but it can help incident responders and SOC analysts during investigations.

Static vs Dynamic analytics
***************************

By default, threat hunting analytics you will create in DeepHunter will be static. They will match a hunting query that is stored in the database, and that will be executed daily by the campaigns cron job.

However, it may happen that part of hunting queries need to be dynamically generated. DeepHunter is shipped with an example (vulnerable_driver_name_detected_loldriver) of such a query. The query for this analytic is dynamically built from a script (``./qm/scripts/vulnerable_driver_name_detected_loldriver.py``) that runs prior to each campaign. This hunting query is built from an updated list of file names matching known vulnerable drivers, published on the LOLDriver website.

Dynamic queries should have the flag "Dyn. query" enabled (which is just an indication, there is no control associated to this flag), to indicate that they should not be manually edited in DeepHunter. Modifications should be done through their corresponding scripts directly.

Architecture
************
.. image:: img/deephunter_architecture.jpg
  :width: 600
  :alt: DeepHunter architecture diagram
