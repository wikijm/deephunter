Reports: Endpoints
##################

Description
***********
This report shows a list of the top 20 endpoints (highest weighted scores) identified in the last campaign.

.. image:: img/reports_endpoints.png
  :width: 1000
  :alt: img

The weighted score is computed as follows:

.. code-block:: sh
  
  last analytic
  for endpoint
      ∑ (relevance x [confidence/4])
  n = 1st analytic
  for endpoint
