wafer-view |Build Status| |PyPi Version|
=======================================================

Wafer map viewer for semi.org XML standards written in Python

Summary
--------

The Wafer-View utility allows a generic XML wafermap file to be viewed. The tool parses the XML and generates bitmap images corresponding to the die status as defined in the wafermap XML file. Each die status can be individually enabled or disabled as well as their colors modified, to easily distinguish where on the wafer any failures occur. Total die, pass/fail, and yield results are also calculated and reported.


Usage
------

From Github
`````````````

Clone the github repository and run `python -m waferview`

.. code-block::

    git clone https://github.com/fronzbot/wafer-view.git
    cd wafer\-view
    pip install -r requirements.txt
    python -m waferview

Any subsequent runs can be performed with `python -m waferview` from the `wafer-view/` repo directory



.. |Build Status| image:: https://github.com/fronzbot/wafer-view/workflows/build/badge.svg
   :target: https://github.com/fronzbot/wafer-view/actions?query=workflow%3Abuild
.. |PyPi Version| image:: https://img.shields.io/pypi/v/wafer-view.svg
    :target: https://pypi.python.org/pypi/wafer-view
