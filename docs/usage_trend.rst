Usage: Trend
############

Trend Analysis
**************
The trend analysis is a special component of threat hunting analytics, to help the threat hunter understand how frequent the analytic triggers. It shows graphs based on statistics collected daily by the campaigns cron job.

.. image:: img/trend_analysis.png
  :width: 1500
  :alt: Trend Analysis

There is a minimum of 2 graphs:
- distribution of number of events
- distribution of number of endpoints (unfiltered)
- optional graphs (depending on the `CUSTOM_FIELDS <settings.html#custom-fields>`_ property), showing the distribution of number of endpoints with custom filters.

The ``see endpoints`` link at the top left corner shows the list of all endpoints matching the current threat hunting analytic.

Anomaly detection
*****************
A z-score mathematical model is applied to the first 2 series (number of hits and number of endpoints) to identify potential statistical anomalies, that are highlighted in red. It is possible to change sensitivity thresholds (click on the ``edit in admin`` link to change threshold values).

- **Anomaly threshold count**: sensitivity threshold for the "number of hits" serie
- **Anomaly threshold endpoints**: sensitivity threshold for the "number of endpoints" serie

Value range from 0 to 3. The higher the less sensitive.
