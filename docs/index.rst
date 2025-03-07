.. DeepHunter documentation master file, created by
   sphinx-quickstart on Sat Dec 14 08:10:40 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the DeepHunter documentation
#######################################

DeepHunter is a Threat Hunting platform that features:

- `Repository <usage_analytics.html>`_ for your threat hunting analytics shown in a sortable table.
- `Search and filters <usage_analytics.html#id4>`_ (description, threat hunting notes, tags, query, OS coverage, vulnerabilities, threat actors, threat names, MITRE coverage, etc.) to find particular threat hunting analytics or group them into hunting packages.
- `Automated execution <intro.html#campaigns>`_ of threat hunting queries in daily campaigns and collection of daily statistics (number of matching events, number of matching endpoints, etc).
- `Trend analysis <usage_trend.html>`_ with automatic detection of statistical anomalies.
- `Timeline view <usage_timeline.html>`_ of the distribution of threat hunting analytics for a given endpoint.
- `Network view <usage_netview.html>`_ module to analyze network activities from a host, with highlights on the destination popularity (based on your environment) and VirusTotal reputation.
- Reports (`Campaigns performance report <reports_stats.html>`_, `Top endpoints identified in the last campaign <reports_endpoints.html>`_, `MITRE coverage <reports_mitre_coverage.html>`_, `List of analytics with missing MITRE coverage <reports_missing_mitre.html>`_)
- Tools (`LOL Driver Hash Checker <tools_lol_drivers_hash_checker.html>`_, `VirusTotal Hash Checker <tools_vt_hash_checker.html>`_, `Whois <tools_whois.html>`_).

.. image:: img/deephunter_analytics.png
  :width: 600
  :alt: DeepHunter Analytics
.. image:: img/trend_analysis.png
  :width: 600
  :alt: DeepHunter Trend Analysis
.. image:: img/timeline.png
  :height: 220
  :alt: DeepHunter Timeline
.. image:: img/reports_endpoints.png
  :height: 220
  :alt: DeepHunter Reports Endpoints
.. image:: img/reports_mitre_coverage.png
  :height: 220
  :alt: DeepHunter Reports MITRE Coverage
.. image:: img/netview.png
  :height: 220
  :alt: DeepHunter Netview
.. image:: img/reports_stats.png
  :height: 220
  :alt: DeepHunter Reports Stats
.. image:: img/tools_vt_hash_checker.png
  :height: 220
  :alt: DeepHunter Tools VT

Contents
########

.. toctree::
   :maxdepth: 2
   :caption: Contents:
  
   intro
   install
   scripts
   authentication
   settings
   usage_login_and_menu
   usage_analytics
   usage_trend
   usage_timeline
   usage_netview
   reports_stats
   reports_perfs
   reports_endpoints
   reports_mitre_coverage
   reports_missing_mitre
   tools_lol_drivers_hash_checker
   tools_vt_hash_checker
   tools_whois
   tools_develop_your_own
   admin
   support
